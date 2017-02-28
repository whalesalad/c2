from py2neo import Graph, cypher

from django.conf import settings
import logging

logger = logging.getLogger('console')

class GraphQuery():
    def __init__(self):
        self.graph = Graph(getattr(settings, "GRAPH_HOST"))
    
    def query_iteratively(self, query_start, max_hops=None):
        self.searched_events = set()
        self.relationships = {}
        self.max_hops = max_hops
        self.hops = 0
        self.relationships = self.check_results(query_start)
        
        return self.relationships

    def check_results(self, query):
        self.hops += 1
        if self.max_hops and self.hops > self.max_hops:
            return self.relationships

        query_string = "MATCH (query_event:Event {event_id: '" + query + "'}) -[r]- (associated_event:Event) RETURN query_event.event_id, r, type(r), r.event_assn_str, associated_event.event_id"
        result = self.graph.cypher.execute(query_string)
        self.searched_events.add(query)

        for item in result:
            event_a = item['query_event.event_id']
            event_b = item['associated_event.event_id']
            r = item['r'].ref
            rel = item['type(r)']
            event_assn_str = item['r.event_assn_str']

            self.relationships[r] = ({'event_a': event_a, 'event_b': event_b, 'rel': rel, 'assn_str': event_assn_str})
            if event_b not in self.searched_events:
                self.relationships.update(self.check_results(event_b))
        return self.relationships

    def get_related_events(self, event_id):
        qry = 'MATCH (e1:Event {event_id: {e1}})-[r*..3]->(e2:Event) RETURN e1, e2, r'
        try:
            res = self.graph.cypher.execute(qry, {'e1': event_id})
            if res:
                return set(sum([[r.e1['event_id'], r.e2['event_id']] for r in res], []))
        except:
            logger.exception('error querying the graph')
