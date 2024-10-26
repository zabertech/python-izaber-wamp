#!/usr/bin/python

"""
This tests if we're able to use the change_user function to switch to another
user on WAMP
"""

import os
from lib import *

from izaber import initialize
from izaber_wamp import wamp

def test_user_swap():
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

    whoami = wamp.call('auth.whoami')
    assert whoami
    assert whoami['authid'] == username

    # Switch the user
    username_2 = 'backend-3'
    password_2 = users[username_2]['plaintext_password']
    wamp.change_user(username_2, password_2)

    whoami = wamp.call('auth.whoami')
    assert whoami
    assert whoami['authid'] == username_2

    # Switch the user with a bad password
    username_2 = 'backend-3'
    password_2 = users[username_2]['plaintext_password'] + 'broken'
    try:
        wamp.change_user(username_2, password_2)
    except Exception:
        pass

if __name__ == "__main__":
    test_user_swap()
