class Sync:
    def __init__(self, name, value=None, setter=None):
        self.name = name
        self.value = value
        self.set = setter

    def on_change(self, value):
        pass

    def change(self, callback):
        self.on_change = callback
        return callback

    def __call__(self):
        self.on_change(self.value)
