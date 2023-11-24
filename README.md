# izaber.wamp

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
2. Change the [`match` option](https://crossbar.io/docs/Registration-Options/#match) so that intead of exact matches, we can do things like prefix or wildcard matches

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
    authrole = details.get('"aller_authrole', '<unknown>')
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

### Publish Example

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

#### Registering A Roster Entry

#### Fetching Roster Entries

## Installation

This library is uploaded to PyPi. Installation for usage can be done with:

`pip install izaber-wamp`

## Development

For hacking on the code, this requires the following:

- `git`
- `python3`
- [poetry](https://python-poetry.org/)

### Setup

```bash
git clone git@github.com:zabertech/python-izaber-wamp.git
cd python-izaber-wamp
poetry install
poetry shell
```

And now it's possible to make changes to the code

### Tests via CLI

As we test on multiple versions of python, getting setup for tests is a bit annoying.

Running on Ubuntu, the setup process is to install the appropriate python versions as well as required support binaries and libraries.

```bash
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt install python3.6 python3.7 python3.8 python3.9 python3.10 libxml2-dev libxslt1-dev build-essential pypy3-dev python3.6-dev python3.7-dev python3.8-dev python3.9-dev python3.10-dev libssl-dev
```

Then running the tests becomes:

```bash
poetry run nox
```

### Tests via Docker

It's not always desireable to pollute the environment with multiple versions of python so a Dockerfile is provided for testing.

```bash
docker build -t tests-izaber-wamp .
docker run tests-izaber-wamp
```

To use the local copy of the library files, can do the following instead:

```bash
docker run --rm -v `pwd`:/python-izaber-wamp tests-izaber-wamp
```

To work in the enviroment try this:

First, run:

```bash
docker run --rm -v `pwd`:/python-izaber-wamp --name 'izaber-wamp' tests-izaber-wamp sleep infinity
```

Then to access:

```bash
docker exec -ti izaber-wamp bash
```

### Packaging

- Ensure that the `pyproject.toml` has the newest version.
- Update the `VERSIONS.md` with the changes made into the library
- Then, assuming access to the pypi account. [Poetry can publish to PyPI](https://python-poetry.org/docs/libraries/#publishing-to-pypi)
    ```bash
    poetry build
    poetry publish
    ```


