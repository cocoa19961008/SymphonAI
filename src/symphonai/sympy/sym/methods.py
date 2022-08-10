from bottle import post, run, request, error
import json
import inspect
import traceback

@error(404)
def error404(error):
    return '{"error": "404 not found", "traceback": ""}'

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
                response = dict(request.json)
                try:
                    return json.dumps(f(*response["args"], **response["kwargs"]))
                except Exception as e:
                    return json.dumps({"error": str(e), "traceback": traceback.format_exc()})

    def run(self):
        self._listen()
        run(host="0.0.0.0", port=80, server='paste', quiet=True)

    def stop(self):
        pass#shutdown()