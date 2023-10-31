import os
import inspect

from izaber import config, app_config, autoloader
from izaber.startup import request_initialize, initializer
from izaber.log import log

from swampyer import WAMPClientTicket

autoloader.add_prefix('izaber.wamp')

__version__ = '3.0.20231030'

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

HOOKS = [
    'connect',
    'join',
    'leave',
    'disconnect',
    'error',
    'unknown',
]

def hook_wrapper(self, hook_name, hook_func):
    def wrapped( *args, **kwargs ):
        if self.hooks and self.hooks.get(hook_name):
            run_parent_hook = False

            # Iterate through all the associated hooks. If one of the hooks
            # returns a Truthy value, we'll invoke the parent function. Normally
            # we're probably trying to run our own handle rather than the parent
            # function (which is why you'd want to hook a handler anyways!)
            for hook_id, hook_fn in self.hooks[hook_name].items():
                if hook_fn(*args, **kwargs):
                    run_parent_hook = True

            # If requested to run the original hook, we do so at the
            # end
            if not run_parent_hook:
                return

        hook_func(*args, **kwargs)
    return wrapped

class IZaberWAMPClientTicket(WAMPClientTicket):

    hooks = None

    def __init__(self):
        self.hooks = {}

        # Wrap the hooks
        for hook_name in HOOKS:
            self.hooks[hook_name] = {}
            fn_name = f"handle_{hook_name}"
            fn = getattr(self, fn_name)
            hooked_fn = hook_wrapper(self, hook_name, fn)
            setattr(self, fn_name, hooked_fn)

        super().__init__()

    def hook(self, handle_name, handle_function):
        """ Adds a function hook to a particular scheme.
        """
        hooks = self.hooks[handle_name]
        hook_id = id(handle_function)
        hooks[hook_id] = handle_function
        return f"{handle_name}:{hook_id}"

    def unhook(self, handle_id):
        """ Removes a hook if setup. The return code is whether
            or not any hook was actually removed. Ignoring the
            error code has no bad impact, the hook will not called
            either way
        """
        (handle_name, hook_id) = handle_id.split(':')
        if handle_name not in self._hook:
            return False
        if handle_id not in self._hook[handle_name]:
            return False
        del self._hook[handle_name][hook_id]
        return True

class WAMP(object):

    def __init__(self,*args,**kwargs):
        self.wamp = IZaberWAMPClientTicket()
        self._original_options = kwargs
        self.configure(**kwargs)

    def configure(self,**kwargs):
        self.wamp.configure(**kwargs)

    def run(self):
        self.wamp.start()
        return self

    def disconnect(self):
        self.wamp.disconnect()

    def reset(self):
        """ Used to reset this particular instance into a state equvalent
            to if this module was just loaded. Useful mostly for testing
        """
        self.wamp = IZaberWAMPClientTicket()
        self.configure(**self._original_options)

    def __getattr__(self,k):
        """ For the most part we just proxy the requests through to the
            underlying swampyer object.
        """
        fn = getattr(self.wamp,k)
        return lambda *a, **kw: fn(
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

    client_options.setdefault('username','')
    client_options.setdefault('password','')
    client_options.setdefault('url','wss://nexus.izaber.com')
    client_options.setdefault('uri_base','com.izaber.wamp')
    client_options.setdefault('realm','izaber')
    client_options.setdefault('authmethods',['ticket'])

    # 5 minute default timeout since we've started to see some longer
    # running functions get hit.
    client_options.setdefault('timeout',60*5)

    wamp.configure(
        **client_options,
        serializers=serializers,
    )

    if AUTORUN and config.wamp.get('run',True):
        wamp.run()



