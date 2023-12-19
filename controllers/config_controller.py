from typing import Union

from fastapi import FastAPI, APIRouter, Header, HTTPException
from starlette import status

from controllers.user_controller import UserController
from models.config import Config


class ConfigController:
    def __init__(self, db_service, config_repo, user_controller: UserController, app: FastAPI):
        self.name = "config"
        self.router = APIRouter()
        self.router.add_api_route(f"/{self.name}/get", self.get_config, methods=["GET"], response_model=Config)

        self.db_service = db_service
        self.config_repo = config_repo
        self.user_controller = user_controller
        app.include_router(self.router)

    def get_config(self, WWW_Authenticate: Union[str, None] = Header(default=None)):
        if self.user_controller.is_user_admin(WWW_Authenticate):
            return self.config_repo.get_configuration()
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Only admin is authorised to see config",
                headers={"WWW-Authenticate": "Bearer"},
            )
