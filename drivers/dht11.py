import Adafruit_DHT


class Hygrometer:
    pin = 17
    sensor = None

    def __init__(self, pin=17):
        self.pin = pin
        self.sensor = Adafruit_DHT.DHT11

    def read(self):
        return Adafruit_DHT.read_retry(self.sensor, self.pin)
