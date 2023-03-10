from pydantic import BaseSettings
import os
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    # Settings
    APP_NAME: str = os.getenv("APP_NAME")
    DEBUG_MODE: bool = os.getenv("DEBUG_MODE")

    # RabbitMQ
    RABBITMQ_HOST: str = os.getenv("RABBITMQ_HOST")
    RABBITMQ_PORT: int = os.getenv("RABBITMQ_PORT")
    RABBITMQ_USER: str = os.getenv("RABBITMQ_USER")
    RABBITMQ_PASS: str = os.getenv("RABBITMQ_PASS")

    # InfluxDB

    INFLUXDB_HOST: str = os.getenv("INFLUXDB_HOST")
    INFLUXDB_PORT: int = os.getenv("INFLUXDB_PORT")
    INFLUXDB_DB: str = os.getenv("INFLUXDB_DB")

    # Uvicorn
    UVICORN_HOST: str = os.getenv("UVICORN_HOST")
    UVICORN_PORT: int = os.getenv("UVICORN_PORT")

    # Kavenegar
    TOKEN: str = os.getenv("TOKEN")
    SENDER: str = os.getenv("SENDER")
    RECIPIENTS: list = os.getenv("RECIPIENTS")
    TEMPLATE: str = os.getenv("TEMPLATE")

    # Gallery
    GALLERY_DIR: str = os.getenv("GALLERY_DIR")

    # Auth
    SECRET_KEY: str = os.getenv("SECRET_KEY")


settings = Settings()
