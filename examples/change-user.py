#!/usr/bin/env python3

"""
This is an example of switching the underlying wamp connection to a different
user's connection. 
"""

from izaber import initialize
from izaber_wamp import wamp

initialize()

# At this point, the `wamp` user will have the default configured user within the 
# izaber.yaml, assuming we have credentials to another user we wish to switch to
# we can do:
another_username = 'user2'
another_password = 'pass2'

try:
    wamp.change_user(another_username, another_password)
    print(wamp.call('auth.whoami'))
except Exception as ex:
    print(f"Oops, that didn't work {ex=}")



