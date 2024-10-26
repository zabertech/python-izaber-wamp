#!/usr/bin/python

"""
This tests if we can create a WAMP session that's separate and apart from the one managed
within the izaber context
"""

import os
from lib import *

from izaber import initialize
from izaber_wamp import wamp, wamp_client_subclass
import swampyer

from swampyer import WAMPClientTicket


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
    wamp2 = wamp.spawn_connection(username_2, password_2)

    whoami = wamp2.call('auth.whoami')
    assert whoami
    assert whoami['authid'] == username_2

    # Switch the user with a bad password
    username_2 = 'backend-3'
    password_2 = users[username_2]['plaintext_password'] + 'broken'
    try:
        wamp3 = wamp.spawn_connection(username_2, password_2)
    except Exception:
        pass

    # The original user should not have been changed
    whoami = wamp.call('auth.whoami')
    assert whoami
    assert whoami['authid'] == username


if __name__ == "__main__":
    test_user_swap()
