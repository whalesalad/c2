import os
import time
import subprocess
import tempfile
import shutil
import pprint

from jinja2 import Environment, FileSystemLoader

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

from c2.accounts.models import User
from c2.sensors.models import Sensor

REMOVE_DIRS = ('.git', '.sass-cache', 'node_modules', 'deploy', 'static', 'bin')
REMOVE_FILES = ('.gitignore', 'Gruntfile.coffee', 'package.json', 'bower.json', 'fabfile.py', 'fabfile.pyc', 'README.md')

class Command(BaseCommand):
    """
    Creates a tarball for server deployments (avoids static asset compilation on prod)
        - grunt build
        - collectstatic
        - copy the current dir to a tempdir
        - delete some stuff we don't want/need going to prod
        - create a deployment tarball

    Fabric will handle pushing this up to the server, extracting, restarting app, etc...
    ** See c2/fabfile.py **

    """

    def get_build_info(self):
        if not self._build_info:
            build_hash = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).strip()
            email = subprocess.check_output(['git', 'config', '--get', 'user.email']).strip()
            name = subprocess.check_output(['git', 'config', '--get', 'user.name']).strip()
            uname = subprocess.check_output(['uname', '-srmnp']).strip()

            self._build_info = {
                'build_hash': build_hash,
                'build_date': time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime()),
                'build_user': { 'name': name, 'email': email, },
                'system_uname': uname
            }

        return self._build_info


    def get_build_file_content(self):
        env = Environment(loader=FileSystemLoader(os.path.join(settings.PROJECT_ROOT, 'deploy')))
        template = env.get_template('build.jinja')
        contents = template.render(self.get_build_info())
        return contents


    def handle(self, *args, **options):
        self._build_info = None

        self.version = self.get_build_info()['build_hash']

        self.stdout.write("Starting build for %s" % self.version)

        self.build_dir = build_dir = tempfile.mkdtemp()
        self.c2_dir = c2_dir = os.path.join(build_dir, 'c2')

        self.wipe_cache()

        # run grunt to clean/build
        self.grunt()

        # Override staticfiles dirs, and run collectstatic
        self.collectstatic()

        call_command('compress', force=True, interactive=False, verbosity=0)

        try:
            self.stdout.write("Building...\n  output => %s" % c2_dir)

            # Copy everything to build_dir/c2
            shutil.copytree(settings.PROJECT_ROOT, c2_dir)

            build_file = open(os.path.join(c2_dir, 'BUILD'), 'w+')
            build_file.write(self.get_build_file_content())
            build_file.close()

            # self.clean_pyc()

            # Copy cached django-compress into public
            static_cache = os.path.join(c2_dir, 'static', 'CACHE')
            public_cache = os.path.join(c2_dir, 'public', 'CACHE')

            try:
                shutil.rmtree(public_cache)
            except OSError:
                pass

            shutil.copytree(static_cache, public_cache)

            shutil.copytree(os.path.join(c2_dir, 'static', 'templates'),
                            os.path.join(c2_dir, 'public', 'templates'))

            try:
                shutil.rmtree(os.path.join(c2_dir, 'public', 'components'))
            except OSError:
                pass

            shutil.copytree(os.path.join(c2_dir, 'static', 'components'),
                            os.path.join(c2_dir, 'public', 'components'))

            # Determine which directories we want to remove
            directories_to_remove = [os.path.join(c2_dir, x) for x in REMOVE_DIRS]

            # Remove those directories
            for d in directories_to_remove:
                try:
                    shutil.rmtree(d)
                except OSError:
                    pass

            files_to_remove = [os.path.join(c2_dir, x) for x in REMOVE_FILES]

            for f in files_to_remove:
                try:
                    os.remove(f)
                except OSError:
                    pass

            archive_dir = os.path.join(settings.PROJECT_ROOT, 'deploy', 'builds')
            archive_dest = os.path.join(archive_dir, 'c2.tar.gz')

            self.stdout.write("Creating tarball...\n  dest => %s" % (archive_dest, ))

            subprocess.Popen(['mkdir', '-p', archive_dir])

            archive = subprocess.Popen(['tar', 'czf', archive_dest, '-C', build_dir, 'c2'], stdout=subprocess.PIPE)
            (output, err) = archive.communicate()

            if err:
                self.stdout.write("  ERROR during tarballing:")
                self.stdout.write(err)

            self.stdout.write("Completed build of %s" % self.version)
        finally:
            # clean up after ourselves...
            shutil.rmtree(c2_dir)
            # pass

    def grunt(self):
        p = subprocess.Popen('grunt', stdout=subprocess.PIPE)
        (output, err) = p.communicate()
        if err:
            self.stdout.write("Error during grunt build:")
            self.stdout.write(err)

    def collectstatic(self):
        settings.STATICFILES_DIRS = ()
        settings.STATIC_ROOT = os.path.join(settings.PROJECT_ROOT, 'public')
        call_command('collectstatic', interactive=False, verbosity=0)

    def clean_pyc(self):
        # find . -name \*.pyc | xargs rm -f
        cmd = "find %s -name \"*.pyc\" -exec rm -rf {} \; " % (self.c2_dir, )
        clean = subprocess.Popen(cmd)
        (output, err) = clean.communicate()

        if err:
            self.stdout.write("/!\ Error during pyc clean:")
            self.stdout.write(err)

    def wipe_cache(self):
        try:
            shutil.rmtree(os.path.join(settings.PROJECT_ROOT, 'static', 'CACHE'))
        except OSError:
            pass
