from datetime import datetime
from typing import Union

from fastapi import FastAPI, APIRouter, Header, HTTPException
from fastapi.encoders import jsonable_encoder
from starlette import status
from starlette.responses import JSONResponse

from controllers.user_controller import UserController
from models.blind import Blind, BlindStates
from repositories.blind_repo import BlindsRepository
from services.service_radio import RadioService
from utils.deserialiser import map_to_blindJson
from utils.printutils import hex_array_to_str, hex_int_to_str, hex_n_array_to_str


class BlindController:
    blind_repo: BlindsRepository
    user_controller: UserController
    radio_service: RadioService

    def __init__(self, db_service, blind_repo, app: FastAPI):
        self.name = "blinds"
        self.db_service = db_service
        self.blind_repo = blind_repo
        self.in_discovery = False
        self.router = APIRouter()
        self.router.add_api_route(f"/{self.name}/indiscovery", self.is_in_discovery, methods=["GET"])
        self.router.add_api_route(f"/{self.name}/indiscovery", self.toggle_discovery, methods=["PUT"])
        self.router.add_api_route(f"/{self.name}/stopbutton", self.add_blind_in_discovery, methods=["POST"])
        self.router.add_api_route(f"/{self.name}/getblinds" + "/{blind}", self.get_blinds, methods=["GET"])
        self.router.add_api_route(f"/{self.name}/getblinds", self.get_blinds, methods=["GET"])
        self.router.add_api_route(f"/{self.name}/action" + "/{blind_id}/{action}", self.set_action, methods=["PUT"])
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

            if blind_from_db.discovery_stop <= 10:
                self.blind_repo.update_stop_count(blind_id=blind_from_db.id, count=blind_from_db.discovery_stop + 1)
                print(f"Blind id: {blind.id} - stopcount: {blind_from_db.discovery_stop + 1}")
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content=jsonable_encoder({"blind_id": blind.id, "stop_count": blind_from_db.discovery_stop + 1,
                                              "last_stop": datetime.utcnow()}),
                )

            else:
                if blind_from_db.time_to_close == 0:
                    if blind_from_db.time_to_close_start is None:
                        self.radio_service.send_command(remote_id=blind_from_db.remote_id, blind_id=blind_from_db.id, channel=blind_from_db.channel, command="Down")
                        self.blind_repo.update_time_to_close_start(datetime.utcnow())

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

    def on_status_update_listener(self, channel, source, destinations, rssi, blind_state):
        print(
            f"Blind status update: chl: {hex_int_to_str(channel)} - src: {hex_array_to_str(source)} - dests: {hex_n_array_to_str(destinations)} - rssi: {rssi} - state: {blind_state}")
        blind_form_db:Blind = self.blind_repo.find_blind_by_id(blind_id=hex_array_to_str(source))
        print(f"STATE FROM DB IS: {blind_form_db.state} / BLIND STATE RCV: {blind_state}")
        if blind_form_db.state == "IN_DISCOVERY" and blind_state.upper() == "MOVINGDOWN":
            print("Updating time_to_close_stop")
            self.blind_repo.update_time_to_close_stop(blind_id=blind_form_db.id, date=datetime.utcnow())
        if blind_form_db.state == "IN_DISCOVERY" and blind_state.upper() == "BOTTOM":
            print("Update time_to_close in time")
            now = datetime.utcnow()
            was = blind_form_db.time_to_close_start
            diff = now - was
            print(f"Time to close: {diff.seconds} seconds")
            self.blind_repo.update_time_to_close_stop(blind_id=blind_form_db.id, date=datetime.utcnow())
            self.blind_repo.update_time_to_close(blind_id=blind_form_db.id, time=diff.seconds)
            self.radio_service.send_command(remote_id=blind_form_db.remote_id, blind_id=blind_form_db.id, channel=blind_form_db.channel, command="Up")
        if blind_form_db.state == "IN_DISCOVERY" and blind_state.upper() == "TOP":
            print("Updating time_to_close_start")
            self.blind_repo.update_time_to_close_start(blind_id=blind_form_db.id, date=datetime.utcnow())
            self.radio_service.send_command(remote_id=blind_form_db.remote_id, blind_id=blind_form_db.id, channel=blind_form_db.channel, command="Down")
        else:
            print(f"Updating to {blind_state.upper()}")
            self.blind_repo.set_status_by_blind_id(blind_id=hex_array_to_str(source), channel=hex_int_to_str(channel),
                                               rssi=rssi, state=blind_state.upper())

    def get_all_blinds(self):
        return self.blind_repo.get_blinds()

    def set_action(self, blind_id: Union[str, None] = None, action: Union[str, None] = None):
        if blind_id is None or action is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Specify a blind and action",
            )

        if not self.blind_exists(blind_id=blind_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Blind doesn't exist",
            )

        blind = self.blind_repo.find_blind_by_id(blind_id=blind_id)

        if action == "open": return self.open_blind(blind=blind)
        if action == "close": return self.close_blind(blind=blind)
        if action == "stop": return self.stop_blind(blind=blind)
        if action == "intermediate": return self.intermediate_blind(blind=blind)
        if action == "tilt": return self.tilt_blind(blind=blind)

    def open_blind(self, blind):
        self.radio_service.send_command(remote_id=blind.remote_id, blind_id=blind.id, channel=blind.channel,
                                        command="Up")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder({"blind_id": blind.id, "action": "open"}),
        )

    def close_blind(self, blind):
        self.radio_service.send_command(remote_id=blind.remote_id, blind_id=blind.id, channel=blind.channel,
                                        command="Down")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder({"blind_id": blind.id, "action": "close"}),
        )

    def stop_blind(self, blind):
        self.radio_service.send_command(remote_id=blind.remote_id, blind_id=blind.id, channel=blind.channel,
                                        command="Stop")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder({"blind_id": blind.id, "action": "stop"}),
        )

    def intermediate_blind(self, blind):
        self.radio_service.send_command(remote_id=blind.remote_id, blind_id=blind.id, channel=blind.channel,
                                        command="Int")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder({"blind_id": blind.id, "action": "intermediate"}),
        )

    def tilt_blind(self, blind):
        self.radio_service.send_command(remote_id=blind.remote_id, blind_id=blind.id, channel=blind.channel,
                                        command="Tilt")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder({"blind_id": blind.id, "action": "tilt"}),
        )

    def get_blinds(self, blind: Union[str, None] = None,
                         WWW_Authenticate: Union[str, None] = Header(default=None)):
        if not self.user_controller.is_user_admin(token=WWW_Authenticate):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User cannot perform this operation",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if blind is None:
            blinds_result = self.get_all_blinds()
            blinds_list = []
            for blind in blinds_result:
                blinds_list.append(map_to_blindJson(blind))
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=jsonable_encoder({"status": "success", "blinds": blinds_list}),
            )
        else:
            if not self.blind_repo.blind_id_exists(blind_id=blind):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Blind not found",
                )
            blind = map_to_blindJson(self.blind_repo.find_blind_by_id(blind_id=blind))
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=jsonable_encoder({"status": "success", "blind": blind}),
            )

    def put_blind_offline(self, blind_id):
        self.blind_repo.set_blind_offline(blind_id=blind_id)
