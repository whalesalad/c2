"""
A processor function is defined below for each Rule in the database.

Each function accepts a two arguments to process:

    rule_config: the RuleConfiguration object which defines the properties
            that the user has defined for his/her rule.

    payload: the event object itself

The function should return an advisory or None based on whether the advisory
was created.
"""
def user_change_rule_processor(rule_config, payload):
    """
    This rule processes users being added/removed/changed.
    """
    pass


def anomalous_package_rule_processer(rule_config, payload):
    """
    Process package anomaly events to see if a candidate is available.
    """
    pass

def anomalous_process_behavior_rule_processor(rule_config, payload):
    """
    Process anomalous process behavior events
    """
    pass

rule_processors = {
    'anomalous_process_behavior': process_anomaly_rule_processor,
    'anomalous_package': anomalous_process_behavior_rule_processor,
    'user_change': user_change_rule_processor,
}

def get_rule_processor(rule_slug):
    return rule_processors.get(rule_slug)