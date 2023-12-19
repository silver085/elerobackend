from typing import Union

from fastapi import APIRouter, FastAPI, Depends, HTTPException, Header
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import BaseModel
from starlette import status
from starlette.responses import JSONResponse

from custom_validators.user_validators import validate_user_create
from models.user import User, PassData
from utils.encryption import encrypt, ENC_SALT
from datetime import datetime, timedelta
from jose import JWTError, jwt

ACCESS_TOKEN_EXPIRE_MINUTES = 14400
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Union[str, None] = None


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class UserController:
    def __init__(self, db_service, user_repo, app: FastAPI):
        self.name = "users"
        self.router = APIRouter()
        self.router.add_api_route(f"/{self.name}/new", self.create_user, methods=["POST"])
        self.router.add_api_route(f"/{self.name}/token", self.login, methods=["POST"], response_model=Token)
        self.router.add_api_route(f"/{self.name}/me", self.read_users_me, methods=["GET"], response_model=User)
        self.router.add_api_route(f"/{self.name}/delete/" + "{id}", self.delete_user, methods=["DELETE"])
        self.router.add_api_route(f"/{self.name}/updateadmin/" + "{id}", self.update_admin, methods=["PATCH"])
        self.router.add_api_route(f"/{self.name}/updatepassword/", self.update_password, methods=["POST"])

        self.db_service = db_service
        self.user_repo = user_repo
        app.include_router(self.router)

    async def create_user(self, user: User):
        try:
            print(f"Request body: {user}")
            result, errors = validate_user_create(user)
            if result:
                return self.user_repo.add_new_user(user)
            else:
                return errors
        except BaseException as e:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=jsonable_encoder({"error": True, "message": f"{e}"}),
            )

    async def delete_user(self, id: int, WWW_Authenticate: Union[str, None] = Header(default=None)):
        if self.is_user_admin(token=WWW_Authenticate):
            if self.user_repo.delete_by_id(id=id):
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content=jsonable_encoder({"result": "Success"})
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No user by that id",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User cannot perform delete operation",
                headers={"WWW-Authenticate": "Bearer"},
            )

    def verify_password(self, clear_password, hashed_password):
        enc_password = encrypt(clear_password, ENC_SALT)
        return enc_password == hashed_password

    def authenticate_user(self, username: str, password: str):
        user = self.user_repo.get_user_record(email=username)
        if not user:
            return False
        if not self.verify_password(password, user.password):
            return False
        return user

    async def login(self, form_data: OAuth2PasswordRequestForm = Depends()):
        user = self.authenticate_user(form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = self.create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        expire = datetime.utcnow() + access_token_expires
        self.user_repo.update_token(user=user, token=access_token, expiry=expire)
        return {"access_token": access_token, "token_type": "bearer"}

    def create_access_token(self, data: dict, expires_delta: Union[timedelta, None] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def get_current_user(self, token: str):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        expired_token = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
            token_data = TokenData(username=username)
        except JWTError:
            raise credentials_exception
        user = self.user_repo.get_user_record(email=token_data.username)
        if user is None:
            raise credentials_exception
        diff = user.token_expires - datetime.utcnow()
        if diff.days > 0:
            return user
        else:
            raise expired_token

    async def read_users_me(self, WWW_Authenticate: Union[str, None] = Header(default=None)):
        return self.get_current_user(token=WWW_Authenticate)

    def is_user_admin(self, token):
        user = self.get_current_user(token)
        return user.is_admin

    def update_admin(self, id, WWW_Authenticate: Union[str, None] = Header(default=None)):
        if self.is_user_admin(token=WWW_Authenticate):
            self.make_admin(id=id)
            user_data = self.user_repo.get_user_by_id(id=id).first()
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=jsonable_encoder({"result": "Success", "is_admin": user_data.is_admin})
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User cannot perform this operation",
                headers={"WWW-Authenticate": "Bearer"},
            )

    def make_admin(self, id):
        user = self.user_repo.get_user_by_id(id=id)
        if user.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user_data = user.first()

        return self.user_repo.update_user(user={
            "id": user_data.id,
            "username": user_data.username,
            "password": user_data.password,
            "email": user_data.email,
            "created_at": user_data.created_at,
            "is_admin": not user_data.is_admin
        })

    async def update_password(self, pass_data: PassData, WWW_Authenticate: Union[str, None] = Header(default=None)):
        user = self.get_current_user(token=WWW_Authenticate)

        if self.verify_password(pass_data.old_password, user.password):
            if pass_data.password == pass_data.repeat_password:
                self.user_repo.update_password(id=user.id, password=encrypt(pass_data.password, ENC_SALT))
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content=jsonable_encoder({"result": "Success"})
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Passwords must match.",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Old password is wrong",
                headers={"WWW-Authenticate": "Bearer"},
            )
