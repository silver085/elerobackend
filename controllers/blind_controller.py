from fastapi import FastAPI, APIRouter
from fastapi.encoders import jsonable_encoder
from starlette import status
from starlette.responses import JSONResponse


class BlindController:
    def __init__(self, db_service, blind_repo, app: FastAPI):
        self.name = "blinds"
        self.db_service = db_service
        self.blind_repo = blind_repo
        self.in_discovery = False
        self.router = APIRouter()
        self.router.add_api_route(f"/{self.name}/indiscovery", self.is_in_discovery, methods=["GET"])
        self.router.add_api_route(f"/{self.name}/indiscovery", self.toggle_discovery, methods=["PUT"])
        app.include_router(self.router)

    def is_in_discovery(self):
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder({"discovery_active": self.in_discovery}),
        )

    def toggle_discovery(self):
        self.in_discovery = not self.in_discovery
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder({"discovery_active": self.in_discovery}),
        )

    def on_stop_button_listener(self, channel, source, destinations):
        if self.in_discovery:
            print(f"Autodiscover blind: C: {channel}. S:{source} , DS:{destinations}")
        else:
            print("Discard, not in discovery.")
