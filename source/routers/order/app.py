from fastapi import FastAPI, responses, Depends
from starlette.exceptions import HTTPException as starletteHTTPException
from source.routers.order.helpers import place_order, check_out
from source.config import settings
from source.message_broker.rabbit_server import RabbitRPC
from source.routers.customer.module.auth import AuthHandler
from source.routers.order.validators.order import check_out
from source.routers.order.helpers.shipment_requests import build_object
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
def checkout( auth_header=Depends(auth_handler.check_current_user_tokens)) -> str:
    """
        all process for creating an order is here
    """
    res = build_object(auth_header)
    a = res
    #
    # if items.type == 'initial':
    #     check_out_result = check_out.check_price_qty(auth_header)
    #     if check_out_result['success']:
    #         pass
    #     else:
    #         return check_out_result['message']
    #
    # elif items.type == 'shipment':
    #     pass
    # elif items.type == 'payment':
    #     pass
    # elif items.type == 'final':
    #     create_order = place_order.place_order(auth_header)
    #
    # return "you entered invalid type"
