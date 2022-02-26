from pydantic import BaseSettings


class Settings(BaseSettings):
    # Settings
    APP_NAME: str
    DEBUG_MODE: bool

    # RabbitMQ
    RABBITMQ_HOST: str
    RABBITMQ_PORT: int
    RABBITMQ_USER: str
    RABBITMQ_PASSWORD: str

    # Uvicorn
    UVICORN_HOST: str
    UVICORN_PORT: int

    # Kavenegar
    TOKEN: str
    SENDER: str
    RECIPIENTS: list
    TEMPLATE: str

    class Config:
        env_file = "../.env"  # get from dotenv file


settings = Settings()
