import fcntl
import socket
import struct

from fastapi import FastAPI, APIRouter
from fastapi.encoders import jsonable_encoder
from starlette import status
from starlette.responses import JSONResponse
from drivers.dht11 import Hygrometer


class DeviceController:
    def __init__(self, app: FastAPI):
        self.hg = Hygrometer()
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
        hm, t = self.hg.read()
        if hm is not None and t is not None:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=jsonable_encoder(
                    {"result": "Success", "temperature": {"value": "{0:0.1f}".format(t), "unit": "°C"},
                     "humidity": {"value": "{1:0.1f}".format(hm), "unit": "%%"}})
            )
        else:
            print("Error: reading from sensor")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=jsonable_encoder({"result": "error", "message": "Unable to read valid results from sensor."})
            )
