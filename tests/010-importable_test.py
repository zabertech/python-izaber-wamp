#!/usr/bin/python

# Does this even import?

def test_loadable():
    import sys
    print("\n\n")
    print("We are using python version:", sys.version)

    import izaber
    import izaber_wamp


test_loadable()
