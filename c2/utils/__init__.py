class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self

def safe_cast(value, cast_to, default=None):
    try:
        value = cast_to(value)
    except:
        value = default
    return value