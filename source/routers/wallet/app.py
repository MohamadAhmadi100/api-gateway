from fastapi import FastAPI, HTTPException, Response, responses
from starlette.exceptions import HTTPException as starletteHTTPException

from source.config import settings
from source.message_broker.rabbit_server import RabbitRPC
from source.routers.pricing.validators.pricing_validator import Price

TAGS = [
    {
        "name": "Pricing",
        "description": "Pricing CRUD"
    }
]
app = FastAPI(
    title="Wallet API",
    description="This is Wallet gateway MicroService",
    version="0.1.0",
    openapi_tags=TAGS,
    docs_url="/api/v1/docs/",
    redoc_url="/api/v1/redoc/",
    debug=settings.DEBUG_MODE
)


@app.exception_handler(starletteHTTPException)
def validation_exception_handler(request, exc):
    return responses.JSONResponse(exc.detail, status_code=exc.status_code)


rpc = RabbitRPC(exchange_name='headers_exchange', timeout=5)
rpc.connect()
rpc.consume()

@app.post("/create", tags=["wallet_create"])
def create_wallet():
    pass
