from operator import itemgetter

class enum_choices(list):
    """
    A helper to create constants from choices tuples.

    Usage:
    SOME_CHOICES = enum_choices(
        FIRST: (1, 'Choice 1'),
        SECOND: (2, 'Choice 2'),
        THIRD: (3, 'Choice 3'),
    )

    It will then return a list with the passed tuples so you can use in the
    Django's fields choices option and, additionally, the returned object will
    have the constant names as attributes (eg. SOME_CHOICES.THIRD == 3).

    """
    def __init__(self, **data):
        for item in sorted(data.items(), key=itemgetter(1)):
            self.append(item[1])
            setattr(self, item[0].upper(), item[1][0])
