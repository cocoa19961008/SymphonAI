from sym import Client

sym = Client()

@sym.subscribe("hello")
def hello(message):
    print(message.decode())

sym.loop()