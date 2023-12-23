import uvicorn as uvicorn
from fastapi import FastAPI



from controllers.blind_controller import BlindController
from controllers.config_controller import ConfigController
from controllers.device_controller import DeviceController
from controllers.user_controller import UserController
from repositories.blind_repo import BlindsRepository
from repositories.config_repo import ConfigRepository
from repositories.user_repo import UsersRepository
from scheduler.BlindsCheck import BlindsCheckerSchedule
from services.service_db import DBService
from services.service_radio import RadioService

app = FastAPI()
db_service = DBService()

user_repo = UsersRepository(dbservice=db_service)
user_controller = UserController(db_service=db_service, user_repo=user_repo, app=app)

config_repo = ConfigRepository(db_service=db_service)
config_controller = ConfigController(db_service=db_service, config_repo=config_repo, user_controller=user_controller, app=app)

radio_service = RadioService(config_controller=config_controller)

blind_repo = BlindsRepository(db_service=db_service)
blind_controller = BlindController(db_service=db_service, blind_repo=blind_repo, app=app)
blind_controller.user_controller = user_controller
radio_service.on_stop_button_cb = blind_controller.on_stop_button_listener
radio_service.on_status_update_cb = blind_controller.on_status_update_listener


blinds_check = BlindsCheckerSchedule()
blinds_check.blind_controller = blind_controller
blinds_check.radio_service = radio_service

radio_service.schedule.append(["Ping radio", blinds_check.ping_blinds])

device_controller = DeviceController(app=app)

try:
    radio_service.start_looping()
    if __name__ == "__main__":
        uvicorn.run(app, host="0.0.0.0", port=8000)
finally:
    radio_service.stop_looping()
    print("Stopped radio.")