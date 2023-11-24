#!/usr/bin/python

from lib import *

from izaber import initialize
from izaber_wamp import wamp, wamp_client_subclass, WAMPClientTicket

IZABER_TEMPLATE = """
default:
  wamp:
    connection:
      url: 'ws://localhost:8282/ws'
      username: '{username}'
      password: '{password}'

"""

@wamp_client_subclass
class HandleJoins(WAMPClientTicket):
    def __init__(self, *args, **kwargs):
        self._join_count = 0
        super().__init__(*args, **kwargs)

    def handle_join(self, *a, **kw):
        self._join_count += 1

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

    # If that worked, let's try logging in
    # via izaber.wamp
    initialize(config={
        'config_filename': str(izaber_fpath)
    }, force=True)

    whoami = wamp.call('auth.whoami')
    assert whoami

    assert wamp._join_count == 1

if __name__ == "__main__":
    test_hook()
