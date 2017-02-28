import os

# determine the environment we want to load
DJANGO_ENV = os.environ.get("DJANGO_ENV", "development")

# load as module
module = __import__(DJANGO_ENV, globals=globals(), fromlist=['c2', 'settings'])

# update globals of this module (i.e. settings) with imported.
globals().update(vars(module))