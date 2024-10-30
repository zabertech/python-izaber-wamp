# izaber.wamp

[[_TOC_]]

## Overview
Base module that brings together most of the requirements to allow WAMP
connectivity within Zaber

## Documentation

### Configuration

This library expects the `izaber.yaml` to be setup with something like the following:

```yaml
default:
  wamp:
    connection:
      url: 'wss://nexus.izaber.com/ws'
      username: 'USERNAME'
      password: 'PASSWORD'
```

Once that's set up, upon calling `izaber.initialize`, the library will eastablish a new WAMP connection.

### Basic Calling Example

In this example, we call a registered function at URI `com.izaber.wamp.auth.whoami`. This is pretty straight-forward:

1. Import `izaber` and `izaber_wamp`
2. Initialize the library with `initialize`
3. Call the function 

Since the `izaber_wamp` library is designed with Zaber mind, the `com.iaber.wamp` can be omitted from the call request like follows:

```python
from izaber import initialize
from izaber_wamp import wamp

initialize()

# Note that wamp.whomi() does the same thing
me = wamp.call('auth.whoami')
print(me)

```

Positional and keyword arguments can be provided after the URI much like a normal python function call.

In the following example, 2 position parameters are provided as well as two keyword arguments:

```python
from izaber import initialize
from izaber_wamp import wamp

initialize()

# Prefix is added to become: com.izaber.wamp.example.call
results = wamp.call('example.call', 'pos1', 'pos2', keyword1='value1', keyword2='value2')
print(results)
```

If for some reason the call fails or the session is not permitted to call that URI, the code will return an error and this library will throw an exception.

### Basic Registration Example

To make URIs that other scripts can call, a script must register a URI. This requires a `backend` role (contact IT to help create an account). Most individual users have a `frontend` role which has pretty restrictive permissions for security reasons.

For this example, the `izaber.yaml` file must be configured with an account that has the `backend` role. Providing that, this code will register the URI `com.izaber.wamp.example.hello`.

The way that's done is to setup the script to receive calls to a particular URI. When called, the nexus server will provide additional information on the call being made including things like exactly *what* the URI (Useful in the case that the registered URI was a pattern match) and which user/role made the call.

```python
import time

from izaber import initialize
from izaber_wamp import wamp

initialize()

def example_hello_fn(event):
    """ Demonstrates creating a registered callable that does not require
        arguments. All registered functions receive a positional parameter `event`
        that holds a swampyer.messages.INVOCATION instance. This object will contain
        metadata details on the call made itself
    """

    # Details will almost always contain a hash such as:
    # {"caller": 8185620139956162, "caller_authid": "zaber", "caller_authrole": "frontend"}
    # In very rare cases (such as trusted component calls), the caller details will
    # not be available as there are no details to be provided.
    details = event.details
    authid = details.get('caller_authid', '<unknown>')
    authrole = details.get('"aller_authrole', '<unknown>')
    return f"Hello {authid} (role: {authrole})!"

registration_id = wamp.register('example.hello', example_hello_fn)
print(registration_id)

while True:
    time.sleep(1)
```

In this example, the service will attempt to remain connected while the code is running. The while loop at the bottom will keep this script running indefinitely. Swampyer in the background, if disconnected, will attempt to reconnect all registrations previously made. To exercise more control on the reconnection process, have a look at the "Hooking `join` for Services" section below.

It is also possible to provide additional connection options when registering via a 3rd argument to `register` or via key `details`. The primary usages for this option are:

1. Is to enable [`force_reregister` option](https://crossbar.io/docs/Registration-Options/#force-reregister) to allow a script to punt other registrations off of a URI. The reason is that sometimes, if a script is aborted (eg. Ctrl-C) the session hangs on for a bit on the server side. Unless we force it, any registered URIs will be held on by the zombied session until timeouts reap it.
2. Change the [`match` option](https://crossbar.io/docs/Registration-Options/#match) so that instead of exact matches, we can do things like prefix or wildcard matches

See [Registration Options](https://crossbar.io/docs/Registration-Options/) in the crossbar documentation.

In the following example we set both the `force_reregister` and `match` options. The `force_reregister` set to `True` will disconnect any other scripts with the same URI. The `match` option set to `prefix` will then match anything below `com.izaber.wamp.hello` (such as `com.izaber.wamp.hello.suboption`)

```python
import time

from izaber import initialize
from izaber_wamp import wamp

initialize()

def example_hello_fn(event):
    """ Demonstrates creating a registered callable that does not require
        arguments. All registered functions receive a positional parameter `event`
        that holds a swampyer.messages.INVOCATION instance. This object will contain
        metadata details on the call made itself
    """

    # Details will almost always contain a hash such as:
    # {"caller": 8185620139956162, "caller_authid": "zaber", "caller_authrole": "frontend", "procedure": "com.izaber.wamp.hello.test"}
    # In very rare cases (such as trusted component calls), the caller details will
    # not be available as there are no details to be provided.
    details = event.details
    authid = details.get('caller_authid', '<unknown>')
    authrole = details.get('caller_authrole', '<unknown>')
    uri = details.get('procedure','<unknown'>)
    return f"Hello {authid} (role: {authrole})! Called from: <{uri}>"

# Register on 'com.izaber.wamp.example.hello'. However, due to the
# 'match': 'prefix', this registration will match all all of the following and more:
# com.izaber.wamp.example.hello.toot
# com.izaber.wamp.example.hello.yep
# com.izaber.wamp.example.hello.this.will.also.work
# The response to the URI, then, can be handled by a single function
# by parsing out the full URI called
registration_id = wamp.register(
                        'example.hello',
                        example_hello_fn,
                        {
                          'force_reregister': True,
                          'match': 'prefix',
                        })
print(registration_id)

while True:
    time.sleep(1)
```

If for some reason it's required to remove the registered function for availability, with the `registration_id`, `unregister` may be called:

```python
wamp.unregister(registration_id)
```

### Publish Example

Scripts can create data and are able to publish the message to a predefined queue. These queues are named similar to the calling URIs and the data published is arbitrary. Publications are fire and forget and if there is no one listening for the information, it will simply be disposed by the nexus server.

This example publishes a hello world message to the `test.sub` URI.

```python
from izaber import initialize
from izaber_wamp import wamp

initialize()

hello_message = {
    "Hello": "World!"
}
wamp.publish('test.sub', hello_message)
```

### Basic Subscription

In this example, this creates a simple subscription to receive push notifications from the server.

```python
from izaber import initialize
from izaber_wamp import wamp

initialize()

def subscribe_event(event, *args, **kwargs):
    print("subscription event:", event)
    print("subscription event received args:", args)
    print("subscription event received keyword args:", kwargs)

sub_id = wamp.subscribe('test.sub', subscribe_event)

time.sleep(10000)
```

### Hooking `join` for Services

If the script is to be a service, that is, a long-running script that registers or acts upon subscription events, then hooking the `join` event will be important. The connection status of the server being independant of the script means the script may end up disconnected from the server at any point.

By hooking the `join` event, when the script manages to reconnect, any actions attached to the `join` will be called meaning it's a good time to reestablish all registrations and subscriptions in a predictably.

In this example, the code will create a registration for `com.izaber.wamp.test.call` and a subscription for `com.izaber.wamp.test.sub`.

```python
#!/usr/bin/env python3

from izaber import initialize
from izaber_wamp import wamp

def test_call(event, *args, **kwargs):
    print(f"Test call called! {args} {kwargs}")

def test_sub(event, *args, **kwargs):
    print(f"Test event called! {args} {kwargs}")

def join_hook(details):
    res = wamp.register('test.call', test_call)
    print(f"Registered test.call with {res}")
    res = wamp.subscribe('test.sub', test_sub)
    print(f"Subscribed test.call with {res}")

# Must be called before the initialize!
wamp.hook('join', join_hook)

initialize()

input("Hit enter to stop service\n")
```

### Roster Example

Rosters allow for clients to register information to a shared name where the information has the same lifetime as the client's connection. Instead of creating a service that collects what is out there for each possible service, Nexus has a roster system built right in.

These are used at Zaber in two locations:

1. Zerp database that are available: Rosters are used as a way to flag under the name `roster.zerp.databases` all the databases available for connection. Previsouly we were using a pub/sub system where available databases had 1s to "report in" that they were available.
2. Dashboards that are active and available: As the dashboard system is mostly decentralized, they are tied together by menus. In the past it would require the first dashboard that connected to the WAMP bus to establish a service that handled the registration of all the dashboards available around Zaber.

So rosters are useful when:

- Information must be shared between a group of scripts
- The information cannot be predetermined (eg. like lists of services that are present)
- The information is only relevant while the client is connected

This makes rosters especially useful when building a system that can flexibly add features and services based upon a "hey who's available to do stuff" paradigm.

#### Registering A Roster Entry

Registering rosters will require a user with backend level permissions. Frontend users can do queries on public records.

This is an example of using rosters to query all services grouped by a keyword

```python
import time
from izaber import initialize, config
from izaber_wamp import wamp

initialize()

ROSTER_KEY = f"roster.example.{config.wamp.connection.username}.test"

# This data is arbitrary primitive data: this can be a list, a dict, a string, a number.
# All nexus does is store and retreive it for applications to do something with so it
# has no expectations for the data aside from it being possible to serialize to JSON
EG_DATA = {
            'random': 'data'
          }

result = wamp.roster_register(ROSTER_KEY, EG_DATA)
print(f"{result=}")

# Sleep for the sake of example. Usually your code may be doing something like waiting for requests
time.sleep(1000)

# We can then delete our roster entry explicity like the following
# or have the system delete it for us when this code eventually disconnects
wamp.roster_unregister(ROSTER_KEY)
```

#### Fetching Roster Entries

Frontend users can do queries on public records.

This is an example of requesting a roster of available services grouped by a keyword

```python
from izaber import initialize, config
from izaber_wamp import wamp

initialize()

ROSTER_KEY = f"roster.example.{config.wamp.connection.username}.test"

# Now we can retreive the data
result2 = wamp.roster_query(ROSTER_KEY)
print(f"{result2=}")
```

### Current User Identity

As a script can be used by multiple users, it will probably be quite helpful to know who was using the script. Along with the fact that it's possible to change the connected user, being able to determine the authenticated identity to Nexus may be tricky. To handle this there is the `whoami()`.

```python
from izaber import initialize, config
from izaber_wamp import wamp

initialize()

print(wamp.whoami())
```

This function will return a dictionary like:

```python
{'authid': 'zaber', 'role': 'frontend'}
```

- `authid` is the crossbar name for the user login
- `role` is the type of user. For now, can be: `frontend`, `backend`, and `trust`. May be extended later with LDAP groupings

### User Metadata (Preferences)

It is possible to store user preferences on nexus so that the information can be shared between across logins. This can be used for things like storing preferences for darkmode or public keys.

```python
from izaber import initialize, config
from izaber_wamp import wamp

initialize()

PREFERENCE_KEY = f"some.preference.key"

# This data is arbitrary primitive data: this can be a list, a dict, a string, a number.
# All nexus does is store and retreive it for applications to do something with so it
# has no expectations for the data aside from it being possible to serialize to JSON
EG_DATA = {
            'random': 'data'
          }

result = wamp.metadata_set(PREFERENCE_KEY, EG_DATA)
print(f"{result=}")

# Now we can retreive the data
result2 = wamp.metadata_get(PREFERENCE_KEY)
print(f"{result2=}")

# Get all the metadata keys associated with the user
result3 = wamp.metadata_list()
print(f"{result3=}")

# We can then delete our metadata entry explicity like the following
# or have the system delete it for us when this code eventually disconnects
wamp.metadata_delete(PREFERENCE_KEY)
```

[Logging in](https://nexus.izaber.com/) will allow you to review, edit, delete what metadata/preferences have already been created in your account as well as creating new entries.

### Switching to another user

While the intention is to allow users to predefine their username and password in `izaber.yaml`, some development patterns request users to login themselves.

Regardless of the pattern used, ensure that passwords never get stored within code.

```python
from izaber import initialize
from izaber_wamp import wamp

initialize()

def print_current_user():
    current_user = wamp.whoami()
    print(current_user["authid"])

# At this point, the `wamp` user will have the default configured user within the
# izaber.yaml, assuming we have credentials to another user we wish to switch to
# we can do:
another_username = 'username'
another_password = 'password'

try:
    print_current_user()
    wamp.change_user(another_username, another_password)
    print_current_user()
except Exception as ex:
    print(f"Oops, that didn't work {ex=}")
```

### Prevent Connection Initialization (Delay Login)

In some cases you may wish to take advantage of the framework without having the system initialize a user by default. Perhaps it's a script that runs, requests the username and password from a user then started performing actions.

In that case, disable the initialization via the `AUTORUN` variable then use the `wamp.change_user(...)` 

```python
from izaber import initialize
from izaber_wamp import wamp
import izaber_wamp

izaber_wamp.AUTORUN = False

initialize()

def print_current_user():
    current_user = wamp.whoami()
    print(current_user["authid"])

another_username = 'zaber'
another_password = 'password'

try:
    wamp.change_user(another_username, another_password)
    print_current_user()
except Exception as ex:
    print(f"Oops, that didn't work {ex=}")
```

### One Time Password (OTP)

One Time Password (OTP) creation can only be performed when the user is connected via username and password, not by username and OTP (or API key). There is a special case where it may be possible generate new OTP passwords while connected via API key but that requires special configuration on Nexus. The reason is that we do not wish malicious scripts grabbing API keys which cascade into additional API key/OTP generations.

OTP can be used in the place of a password for a single-use token for processes or another application to be used within 10 minutes. This really is only useful for specialized applications: Eg for internal applications to transition to another transport (eg: from a python script to web application)

```python
from izaber import initialize
from izaber_wamp import wamp

initialize()

otp = wamp.otp_create()
print(otp)
```

This code, if successful will generate an OTP like:

```python
otp = {
    'uuid': 'EJu2jQqNTW6ey7kBxQVy_Q',
    'origin': 'zaber@10.131.0.122',
    'expires': '2024-10-29T12:32:14.803923-07:00',
    'permissions': [],
    'key': 'zISlv82_mM2zf8Pw3g_NL0lvwvEA1hDaPfAtLDiGufU',
    'owner': 'OgngrWDrRLq56WSEqWj0zQ',
    'plaintext_key': 'voiiG2HVlAajSMUtG3rq2aDIZihfzZFU',
    'login': 'zaber'
}
```

The critical keys in this datastructure is `login` and `plaintext_key` which can be passed into a subsequent connection request.

### API Key Generation

API key creation can only be performed when the user is connected via username and password, not by username and API key (or OTP). There is a special case where it may be possible generate new OTP passwords while connected via API key but that requires special configuration on Nexus. The reason is that we do not wish malicious scripts grabbing API keys which cascade into additional API key/OTP generations.

API keys can be used in the place of a password on individual computers and scripts. This is quite useful from a security perspective since the compromise of a single API key doesn't mean compromise every other system that a user's password may function on.

```python
from izaber import initialize
from izaber_wamp import wamp

initialize()

apikey = wamp.apikeys_create({
                "description": "Purpose of key",
            })
print(apikey)
```

This should return a key like:

```python
{'description': 'Purpose of key',
 'expires': None,
 'key': 'NjzXJN0tEqul9iPxhPdwqL8TdA1nsIxM3_-viuxWVWI',
 'owner': 'OgngrWDrRLq56WSEqWj0zQ',
 'permissions': [],
 'plaintext_key': '1612S4FDxvEY7wep1P62uVtMPru7axPX',
 'uuid': 'pu3tazccR9i8WgxJNJMgeQ'}
```

### List Existing API Keys
API key listing can only be performed when the user is connected via username and password, not by username and API key (or OTP). There is a special case where it may be possible generate new OTP passwords while connected via API key but that requires special configuration on Nexus. The reason is that we do not wish malicious scripts grabbing API keys which cascade into additional API key/OTP generations.

Please note that while currently it's possible to see the plaintext (secret) part of the keys, that will be deprecated in a future update. We currently store both the plaintext and hashed version of the keys. A future update will drop the plaintext key and while it will not impact login, it will mean that the plaintext version will only be available at creation in the future.

```python
from izaber import initialize
from izaber_wamp import wamp
import pprint

initialize()

for apikey in wamp.apikeys_list():
    pprint.pprint(apikey)
```

API keys may be limited to certain calls and even expiry. Example follows where they key is limited to a set of basic URIs.

```python
{'description': '',
 'expires': None,
 'key': 'Akj1238x234kj-2jkah1b234-kjahsdjfb12b31c-45',
 'owner': 'OgngrWDrRLq56WSEqWj0zQ',
 'permissions': [{'perms': 'c',
                  'uri': 'com.izaber.wamp.zerp:testing:testing.attr.type:object.execute.fields_get',
                  'uuid': 'VXrQS6-NR0-ZrorbpH_ktw'},
                 {'perms': 'c',
                  'uri': 'com.izaber.wamp.zerp:testing:testing.attr.type:object.execute.search',
                  'uuid': 'xPwgd6VpSuaPdhMDyuEjHg'},
                 {'perms': 'c',
                  'uri': 'com.izaber.wamp.zerp:testing:testing.attr.type:object.execute.zerp_search_read',
                  'uuid': '2toI4c46S22hDdKSUDyNjw'},
                 {'perms': 'c',
                  'uri': 'com.izaber.wamp.zerp:testing:testing.attr.type:object.execute.read',
                  'uuid': 'cMAv_ooQQOSalV8yr5EFRQ'},
                 {'perms': 'c',
                  'uri': 'com.izaber.wamp.zerp:testing:testing.test.series.type:object.execute.fields_get',
                  'uuid': 'nXlwSHgvTQqSKT0ig1yzqQ'},
                 {'perms': 'c',
                  'uri': 'com.izaber.wamp.zerp:testing:testing.test.series.type:object.execute.search',
                  'uuid': '7sqYP6CrQwavlOCjggJhkw'},
                 {'perms': 'c',
                  'uri': 'com.izaber.wamp.zerp:testing:testing.test.series.type:object.execute.zerp_search_read',
                  'uuid': 'OpA0m5QUQuav2sBzsBmszQ'},
                 {'perms': 'c',
                  'uri': 'com.izaber.wamp.zerp:testing:testing.test.series.type:object.execute.read',
                  'uuid': 'h48MSpChRYOqrlqJvjvAEg'}],
 'plaintext_key': '1233-2343-cvc1-dfgsdfg4234d',
 'uuid': 'gK9PAOGdRsq-72xcoT-95A'}
```

## Installation

This library is uploaded to PyPi. Installation for usage can be done with:

`pip install izaber-wamp`

## Development

For hacking on the code, this requires the following:

- `git`
- `>=python3.8`
- [pdm](https://pdm-project.org/en/latest/)

### Setup

```bash
git clone git@github.com:zabertech/python-izaber-wamp.git
cd python-izaber-wamp
pdm install
```

And now it's possible to make changes to the code

### Tests via Docker

It's not always desireable to pollute the environment with multiple versions of python so using docker compose is the recommend method for testing.

```bash
docker compose up
docker compose logs -f src
```

If you would like to work within the container, have a look at the `docker-compose.yml` and update the `CMD` to `sleep infinity` and it will provide a shell environment (via something like `docker compose exec src bash`) for testing the code within a container.

### Packaging

- Ensure that the `pyproject.toml` has the newest version.
- Update the `VERSIONS.md` with the changes made into the library
- Then, assuming access to the pypi account.
    ```bash
    pdm build
    pdm publish
    ```


