import os
import json

from django import template
from django.conf import settings

register = template.Library()

class ScriptTagsNode(template.Node):
    def __init__(self, file_list):
        self.file_list = file_list
        self.template = u'<script type="text/javascript" src="%s%%s"></script>' % settings.STATIC_URL

    def render(self, context):
        return '\n    '.join((self.template % path) for path in self.file_list)


@register.tag
def script_tags(parser, token):
    tag_name, manifest_file = token.split_contents()
    fp = os.path.join(settings.PROJECT_ROOT, 'public', 'build', manifest_file)

    with open(fp, 'r') as mfo:
        files = json.load(mfo)

    return ScriptTagsNode(files)


