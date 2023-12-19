from datetime import datetime

from sqlalchemy import Table, Column, Integer, String, DateTime, Boolean

from utils.encryption import ENC_SALT
from utils.encryption import encrypt


class UserAlreadyExists(Exception):
    pass


class UserNotExists(Exception):
    pass


class UsersRepository:
    def __init__(self, dbservice):
        self.dbservice = dbservice
        self.users = Table(
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

    def get_user_record(self, email):
        user = self.get_user_by_email(email=email)
        if user.rowcount == 0: return None
        return user.first()

    def get_user_by_email(self, email):
        return self.dbservice.execute_statement(self.users.select().where(self.users.c.email == email))

    def get_user_by_id(self, id):
        return self.dbservice.execute_statement(self.users.select().where(self.users.c.id == id))

    def update_user(self, user):
        statement = self.users.update().values(
            username=user['username'],
            password=user['password'],
            email=user['email'],
            created_at=user['created_at'],
            is_admin=user['is_admin']
        ).where(self.users.c.id == user['id'])
        result = self.dbservice.execute_update(statement)
        return result

    def update_password(self, id, password):
        statement = self.users.update().values(
            password=password
        ).where(self.users.c.id == id)
        result = self.dbservice.execute_update(statement)
        return result

    def add_new_user(self, user):
        if self.get_user_by_email(user.email).rowcount == 0:
            result = self.dbservice.execute_insert(self.users.insert().values(
                username=user.username,
                password=encrypt(user.password, ENC_SALT),
                email=user.email,
                is_admin=False,
                created_at=datetime.utcnow()
            ))

            return {"success": True, "message": "user created"}
        else:
            raise UserAlreadyExists("User already exists.")

    def update_token(self, user, token, expiry):
        statement = self.users.update().values(
            token=token,
            token_expires=expiry
        ).where(self.users.c.id == user.id)
        result = self.dbservice.execute_update(statement)
        return True

    def delete_by_id(self, id):
        if self.get_user_by_id(id=id).rowcount == 0: return False
        statement = self.users.delete().where(self.users.c.id == id)
        result = self.dbservice.execute_update(statement=statement)
        return True
