#!/usr/bin/python

"""
This tests if we can easily manipulate metadata
"""

import os
import random
from lib import *

from izaber import initialize
from izaber_wamp import wamp

def test_rosters():
    snapshot_data = load_nexus_db()
    users = snapshot_data['users']

    # Backend User
    username = 'backend-2'
    password = users[username]['plaintext_password']

    # Let's create an environment based version of the
    # configuration file
    os.environ['IZABER_YAML'] = IZABER_TEMPLATE.format(
                                    username=username,
                                    password=password
                                )

    # If that worked, let's try logging in
    # via izaber.wamp
    initialize(config={
        'config_filename': 'does-not-exist',
    }, force=True)

    # Setup the a roster entry
    data = f"TESTDATA({random.random()})"
    roster_key = 'roster.test.{random.random()}'
    result = wamp.roster_register(roster_key, data)
    assert result

    # Query and get the result
    result2 = wamp.roster_query(roster_key)
    assert result2
    assert result2[0] == data

    # Unregister the roster entry
    result3 = wamp.roster_unregister(roster_key)
    assert result3

    # Verify removal
    result4 = wamp.roster_query(roster_key)
    assert not result4

if __name__ == "__main__":
    test_rosters()



