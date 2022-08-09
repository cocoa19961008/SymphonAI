import paho.mqtt.client as mqtt
import uuid
from sym import sync, methods
import signal
import json
import sys
import requests
import threading

class Client(mqtt.Client):
    def __init__(self, name=f"sym-{uuid.uuid4().hex}"):
        super().__init__(name)
        self.host = "mosquitto"
        #self.username_pw_set(username, password)
        self.subscribers = []
        self.methods = methods.Methods()
        self.syncs = dict()
        signal.signal(signal.SIGTERM, self.on_terminate)

    def on_connect(self, client, userdata, flags, rc):
        print("Connected")
        for sub in self.subscribers:
            super().subscribe(sub["topic"])

            def callback(client, userdata, message):
                sub["callback"](message.payload)
            self.message_callback_add(sub["topic"], callback)

    def connect(self):
        super().connect(self.host)

    def loop(self, block=True):
        self.method_th = threading.Thread(target=self.methods.run)
        self.connect()
        if block:
            super().loop_forever()
        else:
            super().loop_start()

    def on_disconnect(self, client, userdata, rc):
        print("Reconnecting")
        self.connect()

    def subscribe(self, topic):
        def topic_subscribe(callback):
            self.subscribers.append({"topic": topic, "callback": callback})

        return topic_subscribe

    def sync(self, name, value=None, type=str):
        name = f"syncs/{name}"

        def setter(value):
            self.publish(name, value, qos=1, retain=True)
        self.syncs[name] = sync.Sync(name, value, setter)
        @self.subscribe(name)
        def sync_callback(message):
            self.syncs[name].value = type(message.decode())
            self.syncs[name]()

        return self.syncs[name]

    def method(self, callback):
        #name = f"methods/{callback.__name__}"
        self.methods.add_method(callback)

        #def cb(msg):
        #    args = json.loads(msg.decode())
        #    self.publish(name + "/return", json.dumps({"ret": callback(**args)}), qos=2, retain=False)
        #self.subscribers.append({"topic": name, "callback": cb})

    def call(self, target, name):
        def call_method(**args):
            response = requests.post(f"http://{target}/{name}", json=args)
            return response.json()
        return call_method

    def on_terminate(self, signum, frame):
        print("Terminating")
        self.loop_stop()
        self.disconnect()
        self.methods.stop()
        sys.exit(0)
