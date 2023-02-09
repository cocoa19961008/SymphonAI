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
def server(**kwargs):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10), **kwargs)
    server.add_insecure_port('[::]:80')
    return server

def handle_exceptions_here(func):
    def handler(self, request, context):
        try:
            return func(self, request, context)
        except Exception as e:
            traceback.print_exc()
            
            context.abort(grpc.StatusCode.CANCELLED, f"There was an exception in {type(self).__name__}: {type(e).__name__}")
    return handler
