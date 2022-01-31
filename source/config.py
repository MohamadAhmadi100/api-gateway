from pydantic import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "API-Gateway-app"
    DEBUG_MODE: bool = True

    # RabbitMQ
    RABBITMQ_HOST: str = "200.100.100.205"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "rbtmq"
    RABBITMQ_PASSWORD: str = "DeVrab!t123"

    # Uvicorn
    UVICORN_HOST: str = "0.0.0.0"
    UVICORN_PORT: int = 8000

    # Kavenegar
    TOKEN: str = "535041646375714D57613535695561696E7355724A796B2B5657715833434939"
    SENDER: str = "10008663"
    RECIPIENTS: list = ["09025606950", "09113485808", "09123854358"]
    TEMPLATE: str = "service-error"


settings = Settings()
