
from izaber import config, app_config, autoloader
from izaber.startup import request_initialize, initializer
from izaber.log import log

from izaber.wamp.controller import WAMP

autoloader.add_prefix('izaber.wamp')

__version__ = '1.12'

CONFIG_BASE = """
default:
    wamp:
        run: True
        connection:
            username: 'anonymous'
            password: 'changeme'
            url: 'wss://nexus.izaber.com/wss'
"""

AUTORUN = True
wamp = WAMP()

@initializer('wamp')
def load_config(**kwargs):
    request_initialize('config',**kwargs)
    request_initialize('logging',**kwargs)
    config.config_amend_(CONFIG_BASE)

    client_options = config.wamp.connection.dict()

    wamp.configure(
        username=client_options.get('username',u''),
        password=client_options.get('password',u''),
        url=client_options.get('url',u'wss://nexus.izaber.com/ws'),
        uri_base=client_options.get('uri_base',u'com.izaber.wamp'),
        realm=client_options.get('realm',u'izaber'),
        authmethod=client_options.get('authmethod',[u'ticket']),
    )

    if AUTORUN and config.wamp.get('run',True):
        wamp.run()



