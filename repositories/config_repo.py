from sqlalchemy import Table, Column, Integer, String, DateTime, Boolean


class ConfigRepository:
    def __init__(self, db_service):
        self.db_service = db_service
        self.table = Table(
            "config", db_service.meta,
            Column('id', Integer, primary_key=True),
            Column('ssid_name', String),
            Column('ssid_password', String),
            Column('spibus', Integer),
            Column('spics', Integer),
            Column('speed', Integer),
            Column('gdo0', Integer),
            Column('gdo2', Integer),
            Column('retransmit', Integer)
        )
        self.table.create(db_service.connection, checkfirst=True)

    def get_configuration(self):
        statement = self.table.select().where(self.table.c.id == 1)
        result = self.db_service.execute_statement(statement)
        config_data = result.first()
        return  config_data

