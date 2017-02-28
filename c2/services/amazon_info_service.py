import logging
import hashlib
import itertools

from django.core.cache import caches

from boto import ec2

logger = logging.getLogger(__name__)
cache = caches['aws_cache']

class AmazonInfoService(object):
    """

    """
    REGIONS = ['us-west-1', 'us-west-2', 'us-east-1', 'sa-east-1', 'eu-west-1',
               'ap-southeast-2', 'ap-southeast-1', 'ap-northeast-1', ]

    def __init__(self, access_key=None, secret_key=None, regions=None, cache_timeout=None):
        """
        access_key      : the AWS access key
        secret_key      : the AWS secret key
        regions         : a list of regions to check, default is AmazonInfoService.REGIONS
        cache_timeout   : seconds to cache data, 0 or None for no caching.

        """
        self.access_key = access_key
        self.secret_key = secret_key

        self.cache_timeout = int(cache_timeout) if cache_timeout else 0

        self.regions = []

        if regions:
            self.regions = [r for r in regions if r in AmazonInfoService.REGIONS]

        # This is an if not instead of an else on the above case because
        # there is a chance the user did not specify valid regions.
        if not self.regions:
            self.regions = AmazonInfoService.REGIONS

        self._connections = []
        self._instances = []

    def to_dict(self):
        return {
            'instances': self.instances,
            'groups': self.groups
        }

    def cache_key(self, slug):
        regions_hash = hashlib.md5(':'.join(self.regions))
        return ':'.join([self.access_key, regions_hash.hexdigest(), slug, ])

    @property
    def connections(self):
        if not self._connections:
            for region in self.regions:
                self._connections.append(ec2.connect_to_region(region, aws_access_key_id=self.access_key,
                                                                       aws_secret_access_key=self.secret_key))

        return self._connections

    @property
    def is_connected(self):
        return bool(len(self.connections))

    def get_instances(self):
        if not self._instances:
            for conn in self.connections:
                reservations = conn.get_all_reservations()
                self._instances.extend(list(itertools.chain(*[r.instances for r in reservations])))

            self._instances = filter(None, self._instances)

        return self._instances

    def parse_instance(self, i):
        if getattr(i, 'state') in ('terminated', ):
            return None

        keys = ('id', 'public_dns_name', 'private_dns_name', 'state',
                'instance_type', 'ip_address', 'private_ip_address')

        instance = { 'tags': i.tags }

        for key in keys:
            instance[key] = getattr(i, key)

        instance['groups'] = []

        for g in i.groups:
            instance['groups'].append({
                'name': g.name,
                'id': g.id
            })

        return instance


    @property
    def instances(self):
        # TODO wrap this stuff in a decorator. I miss ruby blocks.
        if self.cache_timeout:
            cache_key = self.cache_key('instances')
            cached = cache.get(cache_key, None)

            if cached:
                logger.debug('Found instances for %s in cache.' % cache_key)
                return cached
            else:
                logger.debug('Cache miss for %s' % cache_key)

        response = { getattr(i, 'private_ip_address'): self.parse_instance(i) for i in self.get_instances() if i }

        if self.cache_timeout:
            cache.set(cache_key, response, timeout=self.cache_timeout)

        return response

    def parse_security_group(self, g):
        group = {
            'id': g.id,
            'name': g.name,
            'description': g.description,
            'instances': [i.id for i in g.instances()],
            'tags': g.tags,
            'rules': []
        }

        if 'Name' in g.tags:
            group['title'] = g.tags['Name']
        else:
            group['title'] = None

        for rule in g.rules:
            if rule.ip_protocol == '-1':
                protocol = 'all'
            else:
                protocol = rule.ip_protocol

            group['rules'].append({
                'from_port': str(rule.from_port) if rule.from_port else rule.from_port,
                'to_port': str(rule.to_port) if rule.to_port else rule.to_port,
                'protocol': protocol,
                'grants': [str(g) for g in rule.grants]
            })

        return group

    @property
    def groups(self):
        if self.cache_timeout:
            cache_key = self.cache_key('groups')
            cached = cache.get(cache_key, None)

            if cached:
                logger.debug('Found security groups for %s in cache.' % cache_key)
                return cached
            else:
                logger.debug('Cache miss for %s' % cache_key)

        security_groups = []

        for conn in self.connections:
            parsed = [ self.parse_security_group(g) for g in conn.get_all_security_groups() ]
            for p in parsed:
                p['region'] = conn.region.name
            security_groups.extend(parsed)

        if self.cache_timeout:
            cache.set(cache_key, security_groups, timeout=self.cache_timeout)

        return security_groups

