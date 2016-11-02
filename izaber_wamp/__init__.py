from autobahn_sync import AutobahnSync

from izaber import config, app_config, autoloader
from izaber.startup import request_initialize, initializer
from izaber.log import log

autoloader.add_prefix('izaber.wamp')

__version__ = '1.00'

CONFIG_BASE = """
default:
    wamp:
        connection:
            username: 'anonymous'
            password: 'changeme'
            url: 'wss://nexus.izaber.com/wss'
"""

class WAMP(object):

    def __init__(self,*args,**kwargs):
        self.wamp = AutobahnSync()
        self.configure(*args,**kwargs)

    def configure(self,
                    username=None,
                    password=None,
                    url=None,
                    uri_base=None,
                    realm=None,
                    authmethod=None,
                ):
        if not username is None:
            self.username = unicode(username)
        if not password is None:
            self.password = unicode(password)
        if not url is None:
            self.url = unicode(url)
        if not uri_base is None:
            self.uri_base = unicode(uri_base)
        if not realm is None:
            self.realm = unicode(realm)
        if not authmethod is None:
            self.authmethod = authmethod

    def run(self):
        @self.wamp.on_challenge
        def on_challenge(challenge):
            return self.password
        self.wamp.run(
                    url=self.url,
                    realm=self.realm,
                    authmethods=self.authmethod,
                    authid=self.username,
                )
        return self


    def call(self,uri,*args,**kwargs):
        if self.uri_base:
            uri = u'.'.join([self.uri_base,uri])
        return self.wamp.session.call(uri,*args,**kwargs)

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

    wamp.run()



