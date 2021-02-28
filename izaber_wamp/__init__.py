import os

from izaber import config, app_config, autoloader
from izaber.startup import request_initialize, initializer
from izaber.log import log

from swampyer import WAMPClientTicket

autoloader.add_prefix('izaber.wamp')

__version__ = '2.20210228'

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

class WAMP(object):

    def __init__(self,*args,**kwargs):
        self.wamp = WAMPClientTicket()
        self.configure(**kwargs)

    def configure(self,**kwargs):
        self.wamp.configure(**kwargs)

    def run(self):
        self.wamp.start()
        return self

    def disconnect(self):
        self.wamp.disconnect()

    def __getattr__(self,k):
        if not k in (
                        'call',
                        'leave',
                        'publish',
                        'register',
                        'subscribe'
                    ):
            raise AttributeError("'WAMP' object has no attribute '{}'".format(k))
        fn = getattr(self.wamp,k)
        return lambda uri, *a, **kw: fn(
                        uri,
                        *a,
                        **kw
                    )


AUTORUN = True
wamp = WAMP()

@initializer('wamp')
def load_config(**kwargs):
    request_initialize('config',**kwargs)
    request_initialize('logging',**kwargs)
    config.config_amend_(CONFIG_BASE)

    client_options = config.wamp.connection.dict()

    # Going to default to cbor if possible due to the richness of the
    # data types
    try:
        import cbor
        serializers = client_options.get('serializers',['cbor'])
    except:
        serializers = client_options.get('serializers',['json'])

    wamp.configure(
        username=client_options.get('username',u''),
        password=client_options.get('password',u''),
        url=client_options.get('url',u'wss://nexus.izaber.com/ws'),
        uri_base=client_options.get('uri_base',u'com.izaber.wamp'),
        realm=client_options.get('realm',u'izaber'),
        authmethods=client_options.get('authmethods',[u'ticket']),
        timeout=client_options.get('timeout', 10),
        serializers=serializers,
    )

    if AUTORUN and config.wamp.get('run',True):
        wamp.run()



