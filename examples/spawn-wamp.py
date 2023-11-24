#!/usr/bin/env python3

"""
This is an example of acquiring a new brand new WAMP connection
"""

from izaber import initialize
from izaber_wamp import wamp

initialize()

# At this point, the `wamp` user will have the default configured user within the 
# izaber.yaml, assuming we have credentials to another user we wish to create a
# new wamp client for:
# we can do:
another_username = 'user2'
another_password = 'pass2'

try:
    new_wamp = wamp.spawn_connection(another_username, another_password)

    # This should be the original user
    print(wamp.call('auth.whoami'))

    # This should be the second wamp with the another user signed in
    print(new_wamp.call('auth.whoami'))

except Exception as ex:
    print(f"Oops, that didn't work {ex=}")


