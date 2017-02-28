import hashlib

from django.conf import settings
from django.core.cache import caches

from compressor.filters.base import CompilerFilter

cache = caches['assets']

class CachedCompilerFilter(CompilerFilter):
    commands = settings.COMPRESS_PRECOMPILER_COMMANDS

    def __init__(self, content, attrs, command=None, *args, **kwargs):
        command = self.commands.get(attrs.get('type'))
        super(CachedCompilerFilter, self).__init__(content, command=command, *args, **kwargs)

    def input(self, **kwargs):
        content_hash = hashlib.sha1(self.content.encode('utf8')).hexdigest()

        data = cache.get(content_hash)

        if not data:
            data = super(CachedCompilerFilter, self).input(**kwargs)
            cache.set(content_hash, data, settings.COMPRESS_REBUILD_TIMEOUT)

        return data