import os
import sys
from glob import glob
import importlib


def get_protos():
    sys.path.append("/protos")
    sources = dict()
    for source in os.listdir("/protos"):
        sources[source] = {
            "protos": dict(),
            "msgs": dict()
        }

        for proto in glob(f"/protos/{source}/proto/*pb2.py"):
            proto_name = proto.split("/")[-1][:-3]
            module = ".".join(proto.split("/")[-3:])[:-3]
            sources[source]["protos"][proto_name] = importlib.import_module(module + "_grpc")
            sources[source]["msgs"][proto_name] = importlib.import_module(module)

    for source_name, source in sources.items():
        source["stubs"] = dict()
        source["servicers"] = dict()
        for proto_name, proto in source["protos"].items():
            for var in dir(proto):
                if var.endswith("Stub"):
                    methods = dict()
                    for m in getattr(source["msgs"][proto_name], "_" + var[:-4].upper()).methods:
                        methods[m.name] = {
                            "input": getattr(source["msgs"][proto_name], m.input_type.name),
                            "output": getattr(source["msgs"][proto_name], m.output_type.name)
                        }

                    source["stubs"][var[:-4]] = {
                        "stub": getattr(proto, var),
                        "methods": methods
                    }
                elif var.endswith("Servicer"):
                    methods = dict()
                    for m in getattr(source["msgs"][proto_name], "_" + var[:-8].upper()).methods:
                        methods[m.name] = {
                            "input": getattr(source["msgs"][proto_name], m.input_type.name),
                            "output": getattr(source["msgs"][proto_name], m.output_type.name)
                        }

                    source["servicers"][var[:-8]] = {
                        "servicer": getattr(proto, var),
                        "add_to_server": getattr(proto, f"add_{var}_to_server"),
                        "methods": methods
                    }
    return sources