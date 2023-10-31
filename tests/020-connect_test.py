#!/usr/bin/python

from lib import *

from izaber import initialize
from izaber.wamp import wamp
import swampyer


IZABER_TEMPLATE = """
default:
  wamp:
    connection:
      url: 'ws://localhost:8282/ws'
      username: '{username}'
      password: '{password}'

"""

def test_connect():
    snapshot_data = load_nexus_db()
    users = snapshot_data['users']

    # Try to login manually
    username = 'backend-1'
    password = users[username]['plaintext_password']

    # Do a valid connection
    client = swampyer.WAMPClientTicket(
                url="ws://localhost:8282/ws",
                realm="izaber",
                username=username,
                password=password,
            ).start()
    assert client

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
    initialize('', config={
        'config_filename': str(izaber_fpath)
    })

    # There should now be a wamp connection
    time.sleep(0.3)
    assert wamp.is_connected()

if __name__ == "__main__":
    test_connect()
