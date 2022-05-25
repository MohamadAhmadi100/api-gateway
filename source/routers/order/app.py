from fastapi import FastAPI, HTTPException, Response, responses, Depends, Query
from starlette.exceptions import HTTPException as starletteHTTPException, HTTPException
from  typing  import Union

from source.config import settings
from source.message_broker.rabbit_server import RabbitRPC
from source.routers.cart.app import get_cart
from source.routers.customer.module.auth import AuthHandler
from source.routers.order.helpers.check_out import check_price_qty
from source.routers.order.helpers.place_order import place_order
from source.routers.order.helpers.shipment_requests import shipment_detail
from source.routers.order.validators.order import wallet, payment
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


auth_handler = AuthHandler()


@app.get("/cart_detail/", tags=["get cart detail and checkout"])
def get_cart_detail(response: Response, auth_header=Depends(auth_handler.check_current_user_tokens)) -> dict:
    cart = get_cart(response=response, auth_header=auth_header)
    if not cart['products']:
        return {"success": True, "message": "سبد خرید خالی است"}
    check_out = check_price_qty(auth_header, cart, response)
    if check_out.get("success"):
        return {"success": True, "message": "checkout pass", "response": cart}
    else:
        return {"success": False, "message": check_out.get("message"), "response": cart}


@app.get("/shipment_detail/", tags=["get shipment detail per stocks"])
def get_shipment(response: Response, auth_header=Depends(auth_handler.check_current_user_tokens)) -> dict:
    """
        all process for creating an order is here
    """
    response_result = shipment_detail(auth_header, response)
    if response_result.get("success"):
        response.status_code = response_result.get("status_code")
        return {"success": True, "message": response_result.get("message")}
    else:
        raise HTTPException(status_code=500,
                            detail={"success": False, "message": response_result.get("message")})



@app.put("/add_shipment", tags=["add shipment to cart and get new cart"])
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
                response.status_code = 200
                cart = get_cart(response=response, auth_header=auth_header)
                response.status_code = cart.get("status_code", 200)
                return cart
            raise HTTPException(status_code=cart_response.get("status_code", 500),
                                detail={"error": cart_response.get("error", "Cart service Internal error")})


@app.put("/wallet", tags=["add wallet detail to cart and get new cart"])
def wallet_detail(
        response: Response,
        data: wallet,
        auth_header=Depends(auth_handler.check_current_user_tokens)
):
    user, token_dict = auth_header
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        order_response = rpc.publish(
            message={
                "cart": {
                    "action": "add_wallet_to_cart",
                    "body": {
                        "user_id": data.user_id,
                        "wallet_amount": data.wallet_amount,
                    }
                }
            },
            headers={'cart': True}
        ).get("cart", {})
        if order_response.get("success"):
            cart = get_cart(response=response, auth_header=auth_header)
            response.status_code = cart.get("status_code", 200)
            return cart
        raise HTTPException(status_code=order_response.get("status_code", 500),
                            detail={"error": order_response.get("error", "Order service Internal error")})


@app.put("/payment", tags=["add peyment to cart and get new cart"])
def payment_detail(
        response: Response,
        data: payment,
        auth_header=Depends(auth_handler.check_current_user_tokens)
):
    user, token_dict = auth_header
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        order_response = rpc.publish(
            message={
                "cart": {
                    "action": "add_payment_to_cart",
                    "body": {
                        "user_id": data.user_id,
                        "payment_method": data.payment_method,
                    }
                }
            },
            headers={'cart': True}
        ).get("cart", {})
        if order_response.get("success"):
            cart = get_cart(response=response, auth_header=auth_header)
            response.status_code = cart.get("status_code", 200)
            return cart
        raise HTTPException(status_code=order_response.get("status_code", 500),
                            detail={"error": order_response.get("error", "Order service Internal error")})


@app.put("/final", tags=["final steps and create order"])
def final_order(
        response: Response,
        auth_header=Depends(auth_handler.check_current_user_tokens)
) -> dict:
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        cart = get_cart(response=response, auth_header=auth_header)

        if cart.get('shipment') == {}:
            pass
        elif cart.get('payment') == {}:
            pass
        check_out = check_price_qty(auth_header, cart, response)
        if check_out.get("success"):

            create_order = place_order(auth_header, cart)
            response.status_code = cart.get("status_code")
            if create_order.get("success"):
                pass
        else:
            rpc.publish(
                message={
                    "cart": {
                        "action": "remove_cart",
                        "body": {
                            "user_id": auth_header[0].get("user_id")
                        }
                    }
                },
                headers={'cart': True}
            ).get("cart", {})

            return {"success": False, "message": check_out.get("message"),
                    "response": shipment_detail(auth_header, response)}




@app.get("/orders_list", tags=["Get all orders of customer"])
def get_orders(response: Response,
               order_number: Union[int, None] = Query(default=None),
               date_from: Union[str, None] = Query(default=None),
               date_to: Union[str, None] = Query(default=None),
               auth_header=Depends(auth_handler.check_current_user_tokens)):
    user, token_dict = auth_header
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        order_response = rpc.publish(
            message={
                "order": {
                    "action": "get_customer_orders",
                    "body": {
                        "customerId": user.get("user_id"),
                        "orderNumber": order_number,
                        "dateFrom": date_from,
                        "dateTo": date_to
                    }
                }
            },
            headers={'order': True}
        ).get("order", {})
        if order_response.get("success"):
            response.status_code = order_response.get("status_code", 200)
            return order_response
        raise HTTPException(status_code=order_response.get("status_code", 500),
                            detail={"error": order_response.get("error", "Order service Internal error")})