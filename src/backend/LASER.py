import time
from gpiozero import LED

class LASER:
    def __init__(self, pin=4):
        self.laser = LED(pin, initial_value=False)

    def on(self):
        self.laser.on()

    def off(self):
        self.laser.off()