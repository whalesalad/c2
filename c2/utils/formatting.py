from datetime import datetime
from datetime import timedelta

from c2.utils.helpers import fancy_list_join

def delta2dict(delta):
    """
    Accepts a delta, returns a dictionary of units

    """
    delta = abs(delta)
    return {
        'year'   : int(delta.days / 365),
        'day'    : int(delta.days % 365),
        'hour'   : int(delta.seconds / 3600),
        'minute' : int(delta.seconds / 60) % 60,
        'second' : delta.seconds % 60,
        'microsecond' : delta.microseconds
    }

def human_delta(dt, precision=2, past_tense='{} ago', future_tense='in {}'):
    """Accept a datetime or timedelta, return a human readable delta string"""
    delta = dt

    if type(dt) is not type(timedelta()):
        delta = datetime.now() - dt

    the_tense = past_tense
    if delta < timedelta(0):
        the_tense = future_tense

    d = delta2dict(delta)
    hlist = []
    count = 0
    units = ( 'year', 'day', 'hour', 'minute', 'second' )

    for unit in units:
        if count >= precision: break # met precision
        if d[ unit ] == 0: continue # skip 0's
        s = '' if d[ unit ] == 1 else 's' # handle plurals
        hlist.append( '%s %s%s' % ( d[unit], unit, s ) )
        count += 1

    human_delta = fancy_list_join(hlist)

    return the_tense.format(human_delta)

def human_bytes(num):
    for x in ['bytes','KB','MB','GB']:
        if num < 1024.0:
            return "%3.1f%s" % (num, x)
        num /= 1024.0
    return "%3.1f%s" % (num, 'TB')

def event_delta(baseline_ts, compare_ts):
    """
    This filter is applied to the timestamp of an event. The argument is
    the timestamp of the original event.

    The timedelta is returned.

    """

    if baseline_ts > compare_ts:
        delta = baseline_ts - compare_ts
        return "%s seconds after" % delta.seconds

    delta = compare_ts - baseline_ts

    if delta.seconds == 0:
        return "just before"

    return "%s seconds before" % delta.seconds
