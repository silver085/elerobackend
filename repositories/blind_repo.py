from datetime import datetime

from sqlalchemy import Table, Column, Integer, String, DateTime, Boolean

from models.blind import Blind, BlindStates


class BlindsRepository:
    def __init__(self, db_service):
        self.db_service = db_service
        self.table = Table(
            "blind", db_service.meta,
            Column('id', String(25), primary_key=True),
            Column('name', String(255)),
            Column('remote_id', String(25)),
            Column('channel', String(10)),
            Column('state', String(20)),
            Column('online', Boolean, default=False),
            Column('rssi', Integer, default=0),
            Column('date_added', DateTime, default=datetime.now()),
            Column('is_in_discovery', Boolean, default=0),
            Column('discovery_stop', Integer, default=0),
            Column('last_stop_date', DateTime),
            Column('last_ping', DateTime)
        )
        self.table.create(db_service.connection, checkfirst=True)

    def get_blinds(self):
        statement = self.table.select()
        return self.db_service.execute_statement(statement)

    def find_blind_by_id(self, blind_id):
        statement = self.table.select().where(self.table.c.id == blind_id)
        return self.db_service.execute_statement(statement).first()

    def blind_id_exists(self, blind_id):
        statement = self.table.select().where(self.table.c.id == blind_id)
        return self.db_service.execute_statement(statement).rowcount != 0

    def insert_blind(self, blind: Blind):
        statement = self.table.insert().values(
            id=blind.id,
            name=blind.name,
            remote_id=blind.remote_id,
            channel=blind.channel,
            state=blind.state,
            online=blind.online,
            rssi=blind.rssi,
            date_added=blind.date_added,
            is_in_discovery=blind.is_in_discovery,
            discovery_stop=blind.discovery_stop,
            last_stop_date=blind.last_stop_date
        )
        self.db_service.execute_insert(statement)

    def update_blind(self, blind: Blind):
        statement = self.table.update().values(
            name=blind.name,
            remote_id=blind.remote_id,
            channel=blind.channel,
            state=blind.state,
            online=blind.online,
            rssi=blind.rssi,
            date_added=blind.date_added,
            is_in_discovery=blind.is_in_discovery,
            discovery_stop=blind.discovery_stop,
            last_stop_date=blind.last_stop_date
        ).where(self.table.c.id == blind.id)
        self.db_service.execute_update(statement)

    def update_stop_count(self, blind_id: str, count: int):
        statement = self.table.update().values(
            discovery_stop=count,
            last_stop_date=datetime.utcnow()
        ).where(self.table.c.id == blind_id)
        self.db_service.execute_update(statement)

    def set_blind_not_discovery(self, blind_id: str):
        statement = self.table.update().values(
            discovery_stop=0,
            last_stop_date=datetime.utcnow(),
            online=True,
            is_in_discovery=False,
            state=BlindStates.STATE_STOPPED
        ).where(self.table.c.id == blind_id)
        self.db_service.execute_update(statement)

    def set_status_by_blind_id(self, blind_id: str, channel: str, rssi: int, state: str):
        statement = self.table.update().values(
            rssi=rssi,
            state=state,
            last_ping=datetime.utcnow(),
            online=True
        ).where((self.table.c.id == blind_id) & (self.table.c.is_in_discovery == 0))
        self.db_service.execute_update(statement)

    def set_blind_offline(self, blind_id: str):
        statement = self.table.update().values(
            online=False
        ).where(self.table.c.id == blind_id)
        self.db_service.execute_update(statement)