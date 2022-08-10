import methods
import threading

m = methods.Methods()
def hi():
    print("hi")
m.add_method(hi)

threading.Thread(target=m.run)