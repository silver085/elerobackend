from datetime import datetime

from sqlalchemy import Table, Column, Integer, String, DateTime, Boolean


class BlindsRepository:
    def __init__(self, db_service):
        self.table = Table(
            "blind", db_service.meta,
            Column('id', String(8), primary_key=True),
            Column('name', String(255)),
            Column('remote_id', String(8)),
            Column('state', String(20)),
            Column('online', Boolean, default=False),
            Column('rssi', Integer, default=0),
            Column('date_added', DateTime, default=datetime.now()),
            Column('is_in_discovery', Boolean, default=0),
            Column('discovery_stop', Integer, default=0),
            Column('last_stop_date', DateTime),
        )
        self.table.create(db_service.connection, checkfirst=True)


