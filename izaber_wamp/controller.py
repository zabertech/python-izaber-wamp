from autobahn_sync import AutobahnSync
import os
import certifi

os.environ["SSL_CERT_FILE"] = certifi.where()

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

    def disconnect(self):
        self.wamp.stop()

    def __getattr__(self,k):
        if not k in ('call','leave','publish','register','subscribe'):
            raise AttributeError("'WAMP' object has no attribute '{}'".format(k))
        fn = getattr(self.wamp.session,k)
        return lambda uri, *a, **kw: fn(
                        self.uri_base and u'.'.join([self.uri_base,uri]) or uri,
                        *a,
                        **kw
                    )

