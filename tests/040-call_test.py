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

def hello_example(event, *args, **kwargs):

    print(f"TYPE: {type(event)} event")
    print(f"ARGS: {args}")
    print(f"KWARGS: {kwargs}")

    return {
        'event': {
            'type': type(event).__name__,
        },
        'args': args,
        'kwargs': kwargs,
    }

def test_connect():
    snapshot_data = load_nexus_db()
    users = snapshot_data['users']

    # Backend to create hello
    username = 'backend-1'
    password = users[username]['plaintext_password']

    # Do a valid connection
    swampyer_client = swampyer.WAMPClientTicket(
                url="ws://localhost:8282/ws",
                realm="izaber",
                username=username,
                password=password,
                uri_base='com.izaber.wamp',
            ).start()
    assert swampyer_client

    # Register our function
    swampyer_client.register('hello', hello_example)

    # Calling User
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
    initialize('', config={
        'config_filename': str(izaber_fpath)
    }, force=True)

    # There should now be a wamp connection
    time.sleep(0.3)
    assert wamp.is_connected()

    # Call our function
    hello = wamp.call('hello', 'arg1', keyword1='value1')
    assert hello
    print("????", hello)

if __name__ == "__main__":
    test_connect()
