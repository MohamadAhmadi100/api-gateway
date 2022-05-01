from fastapi import FastAPI, responses, Depends
from starlette.exceptions import HTTPException as starletteHTTPException

from source.config import settings
from source.message_broker.rabbit_server import RabbitRPC
from source.routers.customer.module.auth import AuthHandler
from source.routers.order.validators.order import check_out
TAGS = [
    {
        "name": "Order",
        "description": "ORDER CRUD"
    }
]

app = FastAPI(
    title="Order API",
    description="This is order gateway MicroService",
    version="0.1.0",
    openapi_tags=TAGS,
    docs_url="/docs/",
    redoc_url="/redoc/",
    debug=settings.DEBUG_MODE
)


# customize exception handler of fast api
@app.exception_handler(starletteHTTPException)
def validation_exception_handler(request, exc):
    return responses.JSONResponse(exc.detail, status_code=exc.status_code)


# initialize rabbit mq
rpc = RabbitRPC(exchange_name='headers_exchange', timeout=5)
rpc.connect()
rpc.consume()

auth_handler = AuthHandler()


@app.put("/checkout/", tags=["Cart"])
def checkout(items: check_out, auth_header=Depends(auth_handler.check_current_user_tokens)) -> str:
    """
        all process for creating an order is here
    """
    return "none"



