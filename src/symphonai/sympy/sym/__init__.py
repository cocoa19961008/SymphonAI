import os
from sym.proto import get_protos

sources = get_protos()

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
            return own_servicers[servicer_name]["methods"][m.__name__]["output"](*m(request))
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

    def m(request):
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
            return getattr(s, method)(request)

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