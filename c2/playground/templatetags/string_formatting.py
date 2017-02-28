import pprint
import arrow

from django import template

register = template.Library()

@register.filter(name='unslug')
def format_unslug(value):
    return u' '.join([p.capitalize() for p in value.split('_')])

@register.filter(name='datetime')
def format_datetime(ts):
    return arrow.get(ts).datetime

@register.filter(name='event_delta')
def format_event_delta(ts, compare_ts):
    """
    This filter is applied to the timestamp of an event. The argument is
    the timestamp of the original event.

    The timedelta is returned.

    """

    if ts > compare_ts:
        delta = ts - compare_ts
        return "%s seconds after." % delta.seconds

    delta = compare_ts - ts

    if delta.seconds == 0:
        return "just before."

    return "%s seconds before." % delta.seconds
