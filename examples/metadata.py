#!/usr/bin/env python3

"""
Arbitrary metadata can be stored for a user. This used to be called preferences but since
it can be used for much more than that, it's now called metadata.

"""

from izaber import initialize, config
from izaber_wamp import wamp

initialize()

PREFERENCE_KEY = f"some.preference.key"

# This data is arbitrary primitive data: this can be a list, a dict, a string, a number.
# All nexus does is store and retreive it for applications to do something with so it
# has no expectations for the data aside from it being possible to serialize to JSON
EG_DATA = {
            'random': 'data'
          }

result = wamp.metadata_set(PREFERENCE_KEY, EG_DATA)
print(f"{result=}")

# Now we can retreive the data
result2 = wamp.metadata_get(PREFERENCE_KEY)
print(f"{result2=}")

# Can we get all the metadata keys associated with the user?
result3 = wamp.metadata_list()
print(f"{result3=}")

# We can then delete our metadata entry explicity like the following
# or have the system delete it for us when this code eventually disconnects
wamp.metadata_delete(PREFERENCE_KEY)




