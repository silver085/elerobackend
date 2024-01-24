import fcntl
import socket
import struct

from fastapi import FastAPI, APIRouter
from fastapi.encoders import jsonable_encoder
from starlette import status
from starlette.responses import JSONResponse
import RPi.GPIO as GPIO
import dht11


class DeviceController:
    def __init__(self, app: FastAPI):
        self.name = "device"
        self.router = APIRouter()
        self.router.add_api_route(f"/{self.name}/ping", self.ping, methods=["GET"])
        self.router.add_api_route(f"/{self.name}/hygrometer", self.hygrometer, methods=["GET"])
        app.include_router(self.router)

    def getHwAddr(self, ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        info = fcntl.ioctl(s.fileno(), 0x8927, struct.pack('256s', bytes(ifname, 'utf-8')[:15]))
        return ':'.join('%02x' % b for b in info[18:24])

    def ping(self):
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder(
                {"result": "Success", "status": "online", "device_unique_id": self.getHwAddr("wlan0")})
        )

    def hygrometer(self):
        GPIO.setup(17, GPIO.IN)

        instance = dht11.DHT11(pin=17)
        result = instance.read()
        if result.is_valid():
            print("Temperature: %-3.1f C" % result.temperature)
            print("Humidity: %-3.1f %%" % result.humidity)
            temp = "Temperature: %-3.1f" % result.temperature
            hum = "Humidity: %-3.1f" % result.humidity
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=jsonable_encoder(
                    {"result": "Success", "temperature" : {"value" : temp, "unit" : "°C"}, "humidity" : {"value" : hum, "unit": "%%"}})
            )
        else:
            print("Error: %d" % result.error_code)
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=jsonable_encoder({"result": "error", "message": "Unable to read valid results from sensor."})
            )
