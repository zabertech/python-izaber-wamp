# Versions

## 2.20210228

1. Add support for using alternate serializers. Also will default to `cbor` if available
2. Migrated to using poetry for releases
3. Created Docker based container for testing

## 2.20231031

1. Added ability to add provide alternate Wamp client classes. This makes it possible to
   subclass `handle_join` to have explicit registrations and publications upon join

## 3.0.20231123

1. Added new functionality
  - OTP
  - API Keys
  - Rosters
  - Changing the current WAMP user with new authentication keys
  - Creating a new WAMP session with new keys
