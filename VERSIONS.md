# Versions

## 2.20210228

1. Add support for using alternate serializers. Also will default to `cbor` if available
2. Migrated to using poetry for releases
3. Created Docker based container for testing

## 2.20231031

1. Added ability to add provide alternate Wamp client classes. This makes it possible to
   subclass `handle_join` to have explicit registrations and publications upon join

## 3.0.20231123

1. New version numbering. While it's not breaking changes, as 2.3.XXXX can be less than
   2.2023101 depending on how the compare is implemented, it's a major revision as it will
   start to use an alternate websockets library
2. Uses [websockets](https://github.com/python-websockets/websockets) library rather than
   [python-websocket](https://github.com/websocket-client/websocket-client) by default
3. Uses CBOR by default
4. Added support for nexus-only functions
  - OTP
  - API Keys
  - Rosters
  - Changing the current WAMP user with new authentication keys
  - Creating a new WAMP session with new keys
