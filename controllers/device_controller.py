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

    def ping(self):
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder({"result": "Success", "status": "online"})
        )
