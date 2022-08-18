import time
from bottle import route, post, run, request, error, default_app
import json
import inspect
import traceback
import requests


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

            @route(f"/{name}", method='OPTIONS')
            def method():
                return json.dumps(get_signature(f))

    def run(self):
        self._listen()
        async def run_app():
            print("RUNNING TORNADO")
            from tornado.wsgi import WSGIContainer
            from tornado.httpserver import HTTPServer
            container = WSGIContainer(default_app())
            http_server = HTTPServer(container)
            http_server.listen(80)
            await asyncio.Event().wait()
            print("Listening on port 80")

        #import asyncio
        #asyncio.run(run_app())
        run(host="0.0.0.0", port=80, server="paste")#run(host="0.0.0.0", port=80, server='tornado', quiet=True)

    def stop(self):
        pass#shutdown()

class Call:
    def __init__(self, target, name):
        self.target = target
        self.name = name
        self.enabled = False

    def _wait_for_method(self):
        waiting_for_method = True
        try_num = 0
        while waiting_for_method:
            try_num += 1
            try:
                response = requests.options(f"http://{self.target}/{self.name}")
                return True
            except Exception as e:
                time.sleep(1)
                print(f"Waiting for method {self.name} on {self.target}. Try #{try_num}")
            if try_num >= 30:
                return False

    def enable(self):
        print("Enabling call", self.name, "on", self.target)
        if not self._wait_for_method():
            raise RuntimeError("Failed to enable call", self.name, "on", self.target)
        print("Enabled call", self.name, "on", self.target)
        self.enabled = True

    def __call__(self, *args, **kwargs):
        if not self.enabled:
            self.enable()
        msg = {
            "args": args,
            "kwargs": kwargs
        }
        response = requests.post(f"http://{self.target}/{self.name}", json=msg).json()
        if type(response) is dict:
            if "error" in response:
                print(response["traceback"])
                list_of_kwarg_pairs = [f"{k}={v}" for k, v in kwargs.items()]
                list_of_args = [str(a) for a in args]
                errormsg = f"Exception on call {self.name}({', '.join(list_of_args + list_of_kwarg_pairs)}) on {self.target}: {response['error']}"
                raise RuntimeError(errormsg)
        return response