from bottle import post, run, request
import json
import inspect

def get_signature(f):
    signature = inspect.signature(f)
    method = dict()
    for name, param in signature.parameters.items():
        method[name] = param.default

    return method

class Methods():
    def __init__(self):
        self.methods = dict()

    def add_method(self, f):
        self.methods[f.__name__] = f

    def _listen(self):
        for name, f in self.methods.items():
            @post(f"/{name}")
            def method():
                return json.dumps(f(**dict(request.json)))

    def run(self):
        self._listen()
        run(host="0.0.0.0", port=80, server='paste')

    def stop(self):
        pass#shutdown()