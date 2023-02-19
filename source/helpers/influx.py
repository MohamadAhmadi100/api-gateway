from source.config import settings
from influxdb import InfluxDBClient
from datetime import datetime


class InfluxConnection:
    __slots__ = ["client", "__db", "__instance"]

    @classmethod
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '__instance'):
            cls.__instance = super(InfluxConnection, cls).__new__(cls)
        return cls.__instance

    def __init__(self):
        self.client = InfluxDBClient(
            host=settings.INFLUXDB_HOST,
            port=settings.INFLUXDB_PORT,
            database=settings.INFLUXDB_DB
        )
        self.client.create_database(settings.INFLUXDB_DB)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()

    def monitoring(self, tags, fields):
        self.client.write_points(
            [
                {
                    "measurement": settings.INFLUXDB_DB,
                    "tags": tags,
                    "fields": fields,
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            ]
        )
        return
