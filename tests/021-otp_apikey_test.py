#!/usr/bin/python

from lib import *

from izaber import initialize
from izaber.wamp import wamp

def test_connect():
    snapshot_data = load_nexus_db()
    users = snapshot_data['users']

    # Try to login manually
    username = 'backend-1'
    password = users[username]['plaintext_password']

    # Let's create an environment based version of the
    # configuration file
    os.environ['IZABER_YAML'] = IZABER_TEMPLATE.format(
                                    username=username,
                                    password=password
                                )

    # If that worked, let's try logging in via izaber.wamp
    initialize(config={
        'config_filename': 'does-not-exist',
    }, force=True)

    # There should now be a wamp connection
    time.sleep(0.3)
    assert wamp.is_connected()

    # Let's grab a OTP
    otp = wamp.otp_create()
    assert otp
    assert otp['plaintext_key']
    assert otp['login'] == username

    # Then let's try and login
    client = wamp.spawn_connection(
                username=username,
                password=otp['plaintext_key'],
            )
    assert client

    # There should now be a wamp connection
    time.sleep(0.3)
    assert client.is_connected()

    # We shouldn't be able to create another OTP
    try:
        val = client.otp_create()
        raise Exception("This shouldn't pass")
    except Exception as ex:
        assert re.search(r'is not authorized', str(ex))

    # We won't be able to create another API KEY either
    try:
        val = client.apikeys_create()
        raise Exception("This shouldn't pass")
    except Exception as ex:
        assert re.search(r'is not authorized', str(ex))

if __name__ == "__main__":
    test_connect()
