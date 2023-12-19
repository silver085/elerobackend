import uvicorn as uvicorn
from fastapi import FastAPI

from controllers.config_controller import ConfigController
from controllers.user_controller import UserController
from repositories.config_repo import ConfigRepository
from repositories.user_repo import UsersRepository
from services.service_db import DBService
import threading

from services.service_radio import RadioService

app = FastAPI()
db_service = DBService()

user_repo = UsersRepository(dbservice=db_service)
user_controller = UserController(db_service=db_service, user_repo=user_repo, app=app)

config_repo = ConfigRepository(db_service=db_service)
config_controller = ConfigController(db_service=db_service, config_repo=config_repo, user_controller=user_controller, app=app)

radio_service = RadioService(config_controller=config_controller)

try:
    radio_service.start_looping()
    if __name__ == "__main__":
        uvicorn.run(app, host="0.0.0.0", port=8000)
finally:
    radio_service.stop_looping()
    print("Stopped radio.")