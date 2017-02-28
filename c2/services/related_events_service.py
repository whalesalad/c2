import datetime
import itertools
from functools import wraps

def remove_changed_processes(f):
    def wrapped(*args, **kwargs):
        events = f(*args, **kwargs)
        return list(itertools.ifilterfalse(lambda x: x.key == 'processes' and x.event == 'changed', events))
    return wrapped

class RelatedEventsService(object):
    """

    """

    delta = datetime.timedelta(minutes=5)
    exclude = ('connections', 'memory', 'loadavg', 'sock_stats', 'interface_stats', 'arp', 'uptime', )

    def __init__(self, event):
        self.event = event
        self.start = event.occurred - self.delta
        self.end   = event.occurred + self.delta

    def base_query(self):
        return self.event.__class__.objects.exclude(key__in=self.exclude)

    def before(self):
        events = self.base_query() \
            .filter(sensor=self.event.sensor, occurred__lte=self.end) \
            .order_by('occurred')[:10]

        return events

    @remove_changed_processes
    def after(self):
        events = self.base_query() \
            .filter(sensor=self.event.sensor, occurred__gte=self.start) \
            .order_by('occurred')[:10]

        return events

    @remove_changed_processes
    def all(self):
        events = self.base_query() \
            .filter(sensor=self.event.sensor, occurred__gte=self.start, occurred__lte=self.end) \
            .order_by('occurred')

        return events