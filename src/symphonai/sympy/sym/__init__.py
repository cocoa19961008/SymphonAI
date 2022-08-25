import os
from sym.proto import get_protos

import json
def get_param(varname):
    try:
        return json.loads(os.getenv(varname))
    except:
        return os.getenv(varname)

sources = dict()
try:
    sources = get_protos()
except:
    pass

node_name = os.getenv("SYMNAME")

if node_name in sources:
    own_servicers = sources[node_name]["servicers"]
    servicers = dict()

    for servicer_name, servicer in own_servicers.items():
        class Servicer(servicer["servicer"]):
            def __init__(self):
                super().__init__()
                self._add_to_server = servicer["add_to_server"]
        servicers[servicer_name] = Servicer()

def method(servicer_name):
    def decorator(m):
        if not hasattr(servicers[servicer_name], m.__name__):
            raise NameError(f"Missing proto service definition for function {m.__name__}")

        def call(request, context):
            kwargs = dict()
            for field, value in request.ListFields():
                kwargs[field.name] = value
            return own_servicers[servicer_name]["methods"][m.__name__]["output"](**m(**kwargs))
        setattr(servicers[servicer_name], m.__name__, call)
        
        return m
    return decorator

channels = dict()

TIMEOUT_SEC = 15
def call(target, stub, method):
    if not target in sources:
        raise NameError(f"Cannot find any methods on {target}")
    if not stub in sources[target]["stubs"]:
        raise NameError(f"Cannot find any methods of {stub} on {target}")
    if not method in sources[target]["stubs"][stub]["methods"]:
        raise NameError(f"Cannot find method {method} of {stub} on {target}")

    def m(*args, **kwargs):
        if target not in channels:
            import grpc

            channels[target] = grpc.insecure_channel(f'{target}:50051')

            try:
                grpc.channel_ready_future(channels[target]).result(timeout=TIMEOUT_SEC)
                print("channel connected")
            except grpc.FutureTimeoutError:
                print("channel timed out")

        with channels[target] as channel:
            s = sources[target]["stubs"][stub]["stub"](channel)
            result =  getattr(s, method)(sources[target]["stubs"][stub]["methods"][method]["input"](*args, **kwargs))

            ret = dict()
            for field, value in result.ListFields():
                ret[field.name] = value
            return ret

    return m

def serve(block=True):
    from concurrent import futures
    import grpc

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    import signal
    def stop():
        server.stop(1)
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGHUP, stop)

    for serv in servicers.values():
        serv._add_to_server(serv, server)
    server.add_insecure_port('0.0.0.0:50051')
    server.start()
    if block:
        server.wait_for_termination()
