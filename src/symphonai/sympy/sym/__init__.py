import os

import json
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