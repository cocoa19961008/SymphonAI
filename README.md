<img src="docs/banner.png">

# SymphonAI
SymphonAI is a container intercommunication framework based on gRPC and docker compose that makes it easy to orchestrate AI pipelines or complex structures of multi-agent systems.

# Installation
1. Make sure docker and docker compose plugin are installed:

```bash
sudo apt install docker-ce docker-compose-plugin
```
2. install SymphonAI using pip
```bash
pip3 install git+https://github.com/svenschultze/symphonai
```
3. (OPTIONAL) You may need to add ~/.local/bin to you path by adding this line to your ~/.bashrc and restarting your shell
```bash
export PATH="$HOME/.local/bin:$PATH"
```

# Usage
1. Set up a new Project
```bash
mkdir myproject
cd myproject
sym setup
```
2. Create new nodes *sender* and *receiver* in environment **python3**
```bash
sym create sender python3
sym create receiver python3
```
3. Define the open procedures using the gRPC protobuffer format for each node. Only the node where the procedure is served needs to have to corresponding proto file.

*myproject/src/receiver/proto/receive.proto*
```proto
syntax = "proto3";

service Hello {
  // Sends a greeting
  rpc SayHello (HelloRequest) returns (HelloReply) {}
}

// The request message containing the user's name.
message HelloRequest {
  string name = 1;
}

// The response message containing the greetings
message HelloReply {
  string message = 1;
}
```
4. Build your environments
```bash
sym build
```
5. Now, setup the method and call in the node.py files:

*myproject/src/receiver/node.py*
```python3
import sym

@sym.method("Hello")
def SayHello(name):
    print("Received hello from", name)
    return {
        "message": f"Hello {name}!"
    }

sym.serve()
```

*myproject/src/sender/node.py*
```python3
import sym
import time

SayHello = sym.call("receiver", "Hello", "SayHello")

while True:
  time.sleep(1)
  result = SayHello(name="Sender")
  print(result)
```

6. Start your system
```bash
sym run
```
# Generating Documentation
To generate documentation for all .proto files, run:
```bash
sym docs
```
This will create documentation html files in mypackage/docs/*nodename*