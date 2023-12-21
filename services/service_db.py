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
        self.session = Session(self.engine)

    def execute_statement(self, statement):
        return self.session.execute(statement)

    def execute_insert(self, statement):
        try:
            result = self.session.execute(statement=statement)
            self.session.commit()
            return result.inserted_primary_key
        except RuntimeError as e:
            print(f"Error during execute_insert: {e}")
            return None

    def execute_update(self, statement):
        try:
            result = self.session.execute(statement=statement)
            self.session.commit()
            return True
        except RuntimeError as e:
            print(f"Error during execute_insert: {e}")
            return False