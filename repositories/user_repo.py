from datetime import datetime

from sqlalchemy import Table, Column, Integer, String, DateTime, Boolean

from DTOs.UserData import UserDTO
from models.user import User
from utils.encryption import ENC_SALT
from utils.encryption import encrypt


class UserAlreadyExists(Exception):
    pass


class UserNotExists(Exception):
    pass


class UsersRepository:
    def __init__(self, dbservice):
        self.dbservice = dbservice
        self.table = Table(
            "user", dbservice.meta,
            Column('id', Integer, primary_key=True),
            Column('username', String),
            Column('password', String),
            Column('email', String),
            Column('created_at', DateTime),
            Column('is_admin', Boolean),
            Column('token', String),
            Column('token_expires', DateTime)
        )
        self.table.create(dbservice.connection, checkfirst=True)

    def get_user_record(self, email):
        return self.get_user_by_email(email=email)

    def get_user_by_email(self, email):
        return self.dbservice.session.query(User).filter_by(email=email).first()

    def get_user_by_id(self, id):
        return self.dbservice.session.query(User).get(id)

    def update_user(self, user):
        user_form_db = self.get_user_by_id(id=user.id)
        user_form_db.username = user.username
        user_form_db.password = user.password
        user_form_db.email = user.email
        user_form_db.created_at = user.created_at
        user_form_db.is_admin = user.is_admin
        self.dbservice.session.commit()
        return user_form_db

    def update_password(self, id, password):
        user_from_db = self.get_user_by_id(id=id)
        user_from_db.password = password
        self.dbservice.session.commit()
        return user_from_db

    def add_new_user(self, user: UserDTO):
        if not self.get_user_by_email(user.email):
            new_user = User()
            new_user.email = user.email
            new_user.username = user.username
            new_user.is_admin = False
            new_user.password = encrypt(user.password, ENC_SALT),
            new_user.created_at = datetime.utcnow()
            self.dbservice.session.add(new_user)
            self.dbservice.session.commit()
            return {"success": True, "message": "user created"}
        else:
            raise UserAlreadyExists("User already exists.")

    def update_token(self, user, token, expiry):
        user_from_db = self.get_user_by_id(id=user.id)
        user_from_db.token = token
        user_from_db.token_expires = expiry
        self.dbservice.session.commit()
        return True

    def delete_by_id(self, id):
        user = self.get_user_by_id(id=id)
        if not user: return False
        self.dbservice.session.delete(user)
        self.dbservice.session.commit()
        return True
