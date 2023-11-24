#!/usr/bin/env python3

from izaber import initialize
from izaber_wamp import wamp, wamp_client_subclass, WAMPClientTicket

def test_call(event, *args, **kwargs):
    print(f"Test call called! {args} {kwargs}")

def test_sub(event, *args, **kwargs):
    print(f"Test event called! {args} {kwargs}")

@wamp_client_subclass
class ServiceClient(swampyer.WAMPClientTicket):
    def handle_join(self, *a, **kw):
        res = wamp.register('test.call', test_call)
        print(f"Registered test.call with {res}")
        res = wamp.subscribe('test.sub', test_sub)
        print(f"Subscribed test.call with {res}")

initialize()

input("Hit enter to stop service\n")
