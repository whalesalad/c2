import string
import random
import subprocess

from fabric.api import run

def get_build_hash():
    return subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).strip()

def get_num_procs():
    num = run('nproc').strip()
    return int(num)