from .base import *
from .project import *

# check setting load from live server
# this time all live server mark as production grade
if sys.platform == 'linux':
    from .production import *
else:
    from .development import *


# CACHING SERVER
CACHES['default']['LOCATION'] = REDIS_URL
