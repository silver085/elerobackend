from datetime import datetime

from fastapi import FastAPI, APIRouter
from fastapi.encoders import jsonable_encoder
from starlette import status
from starlette.responses import JSONResponse

from models.blind import Blind, BlindStates
from repositories.blind_repo import BlindsRepository
from utils.printutils import hex_array_to_str, hex_int_to_str


class BlindController:
    blind_repo: BlindsRepository

    def __init__(self, db_service, blind_repo, app: FastAPI):
        self.name = "blinds"
        self.db_service = db_service
        self.blind_repo = blind_repo
        self.in_discovery = False
        self.router = APIRouter()
        self.router.add_api_route(f"/{self.name}/indiscovery", self.is_in_discovery, methods=["GET"])
        self.router.add_api_route(f"/{self.name}/indiscovery", self.toggle_discovery, methods=["PUT"])
        self.router.add_api_route(f"/{self.name}/stopbutton", self.add_blind_in_discovery, methods=["POST"])
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

    def blind_exists(self, blind_id):
        return self.blind_repo.blind_id_exists(blind_id=blind_id)

    def add_blind_in_discovery(self, blind: Blind):
        if not self.blind_exists(blind_id=blind.id):
            self.blind_repo.insert_blind(blind=blind)
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=jsonable_encoder({"blind_id": blind.id, "stop_count": 1, "last_stop": datetime.utcnow()}),
            )

        else:
            blind_from_db: Blind = self.blind_repo.find_blind_by_id(blind_id=blind.id)
            if not blind_from_db.is_in_discovery:
                print(f"Blind {blind_from_db.id} is already configured.")
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content=jsonable_encoder({"blind_id": blind.id, "ready": True}),
                )

            if blind_from_db.discovery_stop < 10:
                self.blind_repo.update_stop_count(blind_id=blind_from_db.id, count=blind_from_db.discovery_stop + 1)
                print(f"Blind id: {blind.id} - stopcount: {blind_from_db.discovery_stop + 1}")
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content=jsonable_encoder({"blind_id": blind.id, "stop_count": blind_from_db.discovery_stop + 1,
                                              "last_stop": datetime.utcnow()}),
                )

            else:
                self.blind_repo.set_blind_not_discovery(blind_from_db.id)
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content=jsonable_encoder({"blind_id": blind.id, "ready": True}),
                )

    def on_stop_button_listener(self, channel, source, destinations):
        if self.in_discovery:
            print(f"Autodiscover blind: C: {channel}. S:{source} , DS:{destinations}")

            for destination in destinations:
                blind = Blind()
                blind.id = hex_array_to_str(destination)
                blind.name = f"Elero Blind {hex_array_to_str(destination)}"
                blind.remote_id = hex_array_to_str(source)
                blind.channel = hex_int_to_str(channel)
                blind.state = BlindStates.STATE_DISCOVERY
                blind.online = True
                blind.date_added = datetime.utcnow()
                blind.is_in_discovery = True
                blind.discovery_stop = 1
                blind.last_stop_date = datetime.utcnow()
                self.add_blind_in_discovery(blind=blind)
        else:
            print("Discard, not in discovery.")
