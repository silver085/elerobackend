import uvicorn as uvicorn
from fastapi import FastAPI

from controllers.user_controller import UserController
from repositories.user_repo import UsersRepository
from services.service_db import DBService

app = FastAPI()
db_service = DBService()

user_repo = UsersRepository(dbservice=db_service)
user_controller = UserController(db_service=db_service, user_repo=user_repo, app=app)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)