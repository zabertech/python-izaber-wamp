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

initialize('')

input("Hit enter to stop service\n")
