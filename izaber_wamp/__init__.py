import os
import copy
import inspect

from izaber import config, app_config, autoloader
from izaber.startup import request_initialize, initializer
from izaber.log import log

import swampyer

autoloader.add_prefix('izaber.wamp')

__version__ = '2.20231030'

CONFIG_BASE = """
default:
    wamp:
        run: True
        connection:
            username: 'anonymous'
            password: 'changeme'
            url: 'wss://nexus.izaber.com/wss'
            serializer: 'cbor'
"""
class WAMPClientTicket(swampyer.WAMPClientTicket):

    ################################################################
    # Misc
    ################################################################

    def whoami(self):
        """ Returns list of active directory users
        """
        return self.call('auth.whoami')

    def ad_users(self):
        """ Returns list of active directory users
        """
        return self.call('ad.users')

    def ad_groups(self):
        """ Returns list of active directory users
        """
        return self.call('ad.groups')

    ################################################################
    # Roster
    ################################################################

    def roster_register(self, roster_key, data, visibility=None):
        return self.call('system.roster.register', roster_key, data, visibility)

    def roster_query(self, roster_key):
        return self.call('system.roster.query', roster_key)

    def roster_unregister(self, roster_key):
        return self.call('system.roster.unregister', roster_key)

    ################################################################
    # Metadata
    ################################################################

    def metadata_set(self, meta_key, value, yaml=False):
        return self.call('my.metadata.set', meta_key, value, yaml)

    def metadata_get(self, meta_key):
        return self.call('my.metadata.get', meta_key)

    def metadata_list(self):
        return self.call('my.metadata.list')

    def metadata_delete(self, uuid_64):
        return self.call('my.metadata.delete', uuid_64)

    ################################################################
    # API KEYS
    ################################################################

    def apikeys_create(self, data_rec=None):
        return self.call('my.apikeys.create', data_rec)

    def apikeys_list(self):
        return self.call('my.apikeys.list')

    def apikeys_delete(self, meta_key):
        return self.call('my.apikeys.delete', meta_key)

    ################################################################
    # OTP
    ################################################################

    def otp_create(self):
        return self.call('my.otps.create')

    def otp_list(self):
        return self.call('my.otps.list')

    def otp_delete(self, uuid_b64):
        return self.call('my.otps.delete', uuid_b64)

# This can be set outside of the library to whatever class is desired
WAMP_CLASS = WAMPClientTicket

# This is a decorator to make the job easier
def wamp_client_subclass(klass):
    global WAMP_CLASS 
    WAMP_CLASS = klass
    return klass

class WAMP(object):
    wamp = None

    def __init__(self, *args, **kwargs):
        self.wamp = None
        self._original_options = kwargs

    def run(self):
        self.wamp.start()
        return self

    def configure(self, **client_options):

        # Going to default to cbor if possible due to the richness of the
        # data types
        serializer = client_options.pop('serializer', None)
        if serializer:
            serializers = [serializer]
        else:
            try:
                import cbor
                serializers = client_options.get('serializers',['cbor'])
            except:
                serializers = client_options.get('serializers',['json'])

        client_options.setdefault('serializers', serializers)
        client_options.setdefault('username','')
        client_options.setdefault('password','')
        client_options.setdefault('url','wss://nexus.izaber.com')
        client_options.setdefault('uri_base','com.izaber.wamp')
        client_options.setdefault('realm','izaber')
        client_options.setdefault('authmethods',['ticket'])

        # 5 minute default timeout since we've started to see some longer
        # running functions get hit.
        client_options.setdefault('timeout', 60*5)

        # Save the connection information
        self._original_options = client_options
        self.wamp.configure(**client_options)

    def reset(self):
        """ Used to reset this particular instance into a state equvalent
            to if this module was just loaded. Useful mostly for testing
        """
        self.wamp = None

    def change_user(self, username, password):
        """ This will dispose and reconnect the local wamp session under
            a different credential
        """
        self.wamp = None
        self._original_options.update({
            'username': username,
            'password': password,
        })
        wamp.reset()
        self.run()
        return self

    def spawn_connection(self, username, password, wamp_class=WAMPClientTicket, **kwargs):
        """ This will spawn a new connection to using the wamp_class provided.
            Note that by default it will be WAMPClientTicket as we do not want
            the join handler to be called
        """
        options = copy.deepcopy(self._original_options)
        options.update({
            'username': username,
            'password': password,
        })
        options.update(kwargs)
        wamp = wamp_class(**options)
        wamp.start()
        return wamp

    def __getattribute__(self,k):
        global WAMP_CLASS 
        # This lets us lazy load the wamp class. We'll try and hold off
        # on instantiating the wamp connection until we really need it
        if k == 'wamp':
            wamp = object.__getattribute__(self, k)
            if not wamp:
                wamp = WAMP_CLASS()
                object.__setattr__(self, 'wamp', wamp)
                self.configure(**self._original_options)
            return wamp
        return object.__getattribute__(self, k)

    def __getattr__(self,k):
        """ For the most part we just proxy the requests through to the
            underlying swampyer object.
        """
        # Then, if we are getting an argument that is not associated with
        # this class directly, we'll just proxy it over to self.wamp
        fn = getattr(self.wamp,k)
        return fn

AUTORUN = True
wamp = WAMP()

@initializer('wamp')
def load_config(**kwargs):
    request_initialize('config',**kwargs)
    request_initialize('logging',**kwargs)
    config.config_amend_(CONFIG_BASE)

    wamp.reset()

    client_options = config.wamp.connection.dict()
    wamp.configure(**client_options)

    if AUTORUN and config.wamp.get('run',True):
        wamp.run()



