from fastapi import FastAPI, responses, Depends, Response
from starlette.exceptions import HTTPException as starletteHTTPException, HTTPException
from source.routers.order.helpers import place_order, check_out
from source.config import settings
from source.message_broker.rabbit_server import RabbitRPC
from source.routers.customer.module.auth import AuthHandler
from source.routers.order.validators.order import check_out
from source.routers.order.helpers.shipment_requests import build_object
from source.routers.shipment.validators.shipment_per_stock import PerStock
from source.routers.cart.helpers.get_cart_helper import get_cart

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


@app.post("/re-initial", tags=["remove cart"])
def test(response: Response, auth_header=Depends(auth_handler.check_current_user_tokens)):
    user, token_dict = auth_header
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        cart_response = rpc.publish(
            message={
                "cart": {
                    "action": "remove_cart",
                    "body": {
                        "user_id": user.get("user_id")
                    }
                }
            },
            headers={'cart': True}
        ).get("cart", {})

        if cart_response.get("success"):
            response.status_code = cart_response.get("status_code", 200)
            return cart_response
        raise HTTPException(status_code=cart_response.get("status_code", 500),
                            detail={"error": cart_response.get("error", "Cart service Internal error")})



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