import json

from django import template

from c2.utils.json_encoders import DecimalEncoder

register = template.Library()

@register.filter(name='json')
def format_json(value):
    return json.dumps(value, sort_keys=True, indent=2, separators=(',', ': '), cls=DecimalEncoder)