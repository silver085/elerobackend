from contextlib import contextmanager

from sqlalchemy import create_engine, MetaData
from sqlalchemy.exc import PendingRollbackError
from sqlalchemy.orm import Session, sessionmaker

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
        try:
            self.session_scope()
            res = self.session.execute(statement)
            self.session_scope()
            return res
        except PendingRollbackError:
            self.session.rollback()

    def execute_insert(self, statement):
        try:
            result = self.session.execute(statement=statement)
            self.session_scope()
            return result.inserted_primary_key
        except RuntimeError as e:
            print(f"Error during execute_insert: {e}")
            return None

    def execute_update(self, statement):
        try:
            result = self.session.execute(statement=statement)
            self.session_scope()
            return True
        except RuntimeError as e:
            print(f"Error during execute_insert: {e}")
            return False

    @contextmanager
    def session_scope(self):
        self.engine = create_engine(
            f"mysql+mysqldb://{db_config['user']}:{db_config['passwd']}@{db_config['host']}/{db_config['db']}",
            pool_pre_ping=True)  # echo=True if needed to see background SQL
        Session = sessionmaker(bind=self.engine)
        session = Session()
        try:
            # this is where the "work" happens!
            yield session
            # always commit changes!
            session.commit()
        except:
            # if any kind of exception occurs, rollback transaction
            session.rollback()
            raise
        finally:
            session.close()
