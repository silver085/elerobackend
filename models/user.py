from sqlalchemy import Integer, String, DateTime, Boolean
from sqlalchemy.orm import mapped_column, DeclarativeBase


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user"
    id = mapped_column(Integer, primary_key=True)
    username = mapped_column(String)
    password = mapped_column(String)
    email = mapped_column(String)
    created_at = mapped_column(DateTime)
    is_admin = mapped_column(Boolean)
    token_expires = mapped_column(String)


