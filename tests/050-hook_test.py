#!/usr/bin/python

from lib import *

from izaber import initialize
from izaber.wamp import wamp
from izaber.startup import initialization_rack
import swampyer

IZABER_TEMPLATE = """
default:
  wamp:
    connection:
      url: 'ws://localhost:8282/ws'
      username: '{username}'
      password: '{password}'

"""

def hello_example(event, *args, **kwargs):
    print(f"TYPE: {type(event)} event")
    print(f"ARGS: {args}")
    print(f"KWARGS: {kwargs}")

def test_hook():
    snapshot_data = load_nexus_db()
    users = snapshot_data['users']

    # Backend User
    username = 'backend-2'
    password = users[username]['plaintext_password']

    # Let's create a local version of the
    # izaber.yaml file
    izaber_fpath = TEST_PATH / 'izaber.yaml'
    izaber_fh = izaber_fpath.open('w')
    izaber_fh.write(
        IZABER_TEMPLATE.format(
            username=username,
            password=password
        )
    )
    izaber_fh.close()

    # Attach our join hook
    JOIN_CALLS = []
    def join_hook(details):
        JOIN_CALLS.append(details)

    assert not JOIN_CALLS
    wamp.hook('join', join_hook)

    # Attach our disconnect hook
    DISCONNECTS = []
    def disconnect_hook(details):
        DISCONNECTS.append(details)
    wamp.hook('disconnect', disconnect_hook)
    assert not DISCONNECTS

    # If that worked, let's try logging in
    # via izaber.wamp
    initialize(config={
        'config_filename': str(izaber_fpath)
    }, force=True)

    # There should now be a wamp connection
    time.sleep(0.3)
    assert wamp.is_connected()

    time.sleep(2)

    # Verify that the `join_hook` has been called
    assert JOIN_CALLS

    # Disconnect our client
    assert not DISCONNECTS
    wamp.

if __name__ == "__main__":
    test_hook()
