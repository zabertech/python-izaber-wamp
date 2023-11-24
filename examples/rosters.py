#!/usr/bin/env python3

"""
Roster data is information that can be stored publically on the nexus server
for public retrieval and have a max lifetime of the session. This is handy
when trying to create things that can be extended

Registering rosters will require a user with backend level permissions. Frontend users
can do queries on public records.

This is an example of using rosters to query all services grouped by a keyword

Places where this functionality might be useful:

- dashboards
- zerp databases (not yet)
- users with active chat sessions
- etc

"""

from izaber import initialize, config
from izaber_wamp import wamp

initialize()

ROSTER_KEY = f"roster.example.{config.wamp.connection.username}.test"

# This data is arbitrary primitive data: this can be a list, a dict, a string, a number.
# All nexus does is store and retreive it for applications to do something with so it
# has no expectations for the data aside from it being possible to serialize to JSON
EG_DATA = {
            'random': 'data'
          }

result = wamp.roster_register(ROSTER_KEY, EG_DATA)
print(f"{result=}")

# Now we can retreive the data
result2 = wamp.roster_query(ROSTER_KEY)
print(f"{result2=}")

# We can then delete our roster entry explicity like the following
# or have the system delete it for us when this code eventually disconnects
wamp.roster_unregister(ROSTER_KEY)

