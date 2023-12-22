import fcntl
import struct
from socket import socket

from fastapi import FastAPI, APIRouter
from fastapi.encoders import jsonable_encoder
from starlette import status
from starlette.responses import JSONResponse


class DeviceController:
    def __init__(self, app: FastAPI):
        self.name = "device"
        self.router = APIRouter()
        self.router.add_api_route(f"/{self.name}/ping", self.ping, methods=["GET"])
        app.include_router(self.router)

    def getHwAddr(self, ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        info = fcntl.ioctl(s.fileno(), 0x8927, struct.pack('256s', ifname[:15]))
        return ':'.join(['%02x' % ord(char) for char in info[18:24]])

    def ping(self):
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder({"result": "Success", "status": "online", "device_unique_id" : self.getHwAddr("wlan0")})
        )
