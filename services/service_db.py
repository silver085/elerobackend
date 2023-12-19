from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import Session

from config.db import db_config
import sys


class DBService:

    def __init__(self):
        self.engine = create_engine(
            f"mysql+mysqldb://{db_config['user']}:{db_config['passwd']}@{db_config['host']}/{db_config['db']}")
        self.meta = MetaData()
        self.meta.create_all(self.engine)
        self.connection = self.engine.connect()

    def execute_statement(self, statement):
        return self.connection.execute(statement)

    def execute_insert(self, statement):
        result = self.connection.execute(statement=statement)
        self.connection.commit()
        return result.inserted_primary_key

    def execute_update(self, statement):
        result = self.connection.execute(statement=statement)
        self.connection.commit()
