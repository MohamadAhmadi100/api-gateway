from pydantic import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "API Gateway app"

    # RabbitMQ
    RABBITMQ_HOST: str = "200.100.100.205"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "rbtmq"
    RABBITMQ_PASSWORD: str = "DeVrab!t123"

    # Uvicorn
    UVICORN_HOST: str = "0.0.0.0"
    UVICORN_PORT: int = 8000


settings = Settings()
