#!/usr/bin/python

"""
This tests if we can easily manipulate metadatas
"""

import os
import random
from lib import *

from izaber import initialize
from izaber_wamp import wamp

def test_metadatas():
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

    # Setup the a metadata entry
    data = f"TESTDATA({random.random()})"
    metadata_key = 'metadata.test.{random.random()}'
    result = wamp.metadata_set(metadata_key, data)
    assert result

    # Query and get the result
    result2 = wamp.metadata_get(metadata_key)
    assert result2 == data

    # Get everything
    result3 = wamp.metadata_list()
    import pprint
    pprint.pprint(result3)
    assert result3

    # Unregister the metadata entry
    wamp.metadata_delete(metadata_key)

    # Verify removal
    result4 = wamp.metadata_get(metadata_key)
    assert not result4

if __name__ == "__main__":
    test_metadatas()
