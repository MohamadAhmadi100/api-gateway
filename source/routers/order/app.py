from fastapi import FastAPI, responses, Depends, Response
from starlette.exceptions import HTTPException as starletteHTTPException, HTTPException

from source.config import settings
from source.message_broker.rabbit_server import RabbitRPC
from source.routers.cart.helpers.get_cart_helper import get_cart
from source.routers.customer.module.auth import AuthHandler
from source.routers.order.helpers.initial_data import initial
from source.routers.shipment.validators.shipment_per_stock import PerStock

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


@app.get("/initial/", tags=["Cart"])
def initial_order(auth_header=Depends(auth_handler.check_current_user_tokens)) -> str:
    """
        all process for creating an order is here
    """
    response = initial(auth_header)
    return response

@app.put("/add", tags=["add shipment to cart and get new cart"])
def shipment_per_stock(
        response: Response,
        data: PerStock,
        auth_header=Depends(auth_handler.check_current_user_tokens)
):
    user, token_dict = auth_header
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        shipment_response = rpc.publish(
            message={
                "shipment": {
                    "action": "get_selected_method",
                    "body": {
                        "data": data.json()
                    }
                }
            },
            headers={'shipment': True}
        ).get("shipment", {})
        if shipment_response.get("success"):
            rpc.response_len_setter(response_len=1)
            cart_response = rpc.publish(
                message={
                    "cart": {
                        "action": "add_shipment_to_cart",
                        "body": {
                            "shipment": {
                                "shipment_details": shipment_response.get("message"),
                                "user_id": user.get("user_id")
                            }
                        }
                    }
                },
                headers={'cart': True}
            ).get("cart", {})

            if cart_response.get("success"):
                cart = get_cart(user)
                response.status_code = cart.get("status_code", 200)
                return cart
            raise HTTPException(status_code=cart_response.get("status_code", 500),
                                detail={"error": cart_response.get("error", "Cart service Internal error")})

