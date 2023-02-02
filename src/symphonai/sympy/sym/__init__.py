import os
import traceback
import json
import grpc

def get_param(varname):
    try:
        return json.loads(os.getenv(varname))
    except:
        return os.getenv(varname)


import grpc
import grpc.experimental
def get_proto(package):
    return grpc.protos_and_services(f"protos/{package}.proto")

from concurrent import futures
def server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    server.add_insecure_port('[::]:80')
    return server

def handle_exceptions_here(func):
    def handler(self, request, context):
        try:
            return func(self, request, context)
        except:
            traceback.print_exc()
            context.abort(grpc.StatusCode.CANCELLED, "There was an exception")
        return