from fastapi import FastAPI, HTTPException, Response, responses, Depends, Query
from starlette.exceptions import HTTPException as starletteHTTPException, HTTPException
from typing import Union

from source.config import settings
from source.helpers.case_converter import convert_case
from source.message_broker.rabbit_server import RabbitRPC
from source.routers.customer.helpers.profile_view import get_profile_info
from source.routers.cart.app import get_cart
from source.routers.customer.module.auth import AuthHandler
from source.routers.order.helpers.check_out import check_price_qty
from source.routers.order.helpers.place_order import place_order
from source.routers.order.helpers.shipment_requests import shipment_detail, check_shipment_per_stock
from source.routers.order.validators.order import wallet, payment
from source.routers.payment.app import get_url
from source.routers.shipment.validators.shipment_per_stock import PerStock
from source.routers.payment.validators.payment import SendData
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
        cart = get_cart(response=response, auth_header=auth_header)
        return {"success": False, "message": check_out.get("message"), "response": cart}


@app.get("/shipment_detail/", tags=["shipment for order"])
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


@app.get("/payment_detail_official/", tags=["payment for order"])
def get_payment_official(response: Response, auth_header=Depends(auth_handler.check_current_user_tokens)) -> dict:
    """
        payment and wallet detail for creating payment step
    """
    user, token = auth_header
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        try:
            cart = get_cart(response=response, auth_header=auth_header)

            # check if customer select all the shipment methods per stock
            check_shipment_result = check_shipment_per_stock(cart)
            if len(cart['shipment']) != len(check_shipment_result):
                return {"success": False, "message": "!روش ارسال برای همه انبار ها را انتخاب کنید"}

            rpc.response_len_setter(response_len=1)
            wallet_response = rpc.publish(
                message={
                    "wallet": {
                        "action": "get_wallet_by_customer_id",
                        "body": {
                            "customer_id": user.get("user_id")
                        }
                    }
                },
                headers={'wallet': True}
            ).get("wallet", {})
            wallet_amount = 0
            if wallet_response.get("success"):
                wallet_amount = wallet_response['message'].get('remainingAmount')
            if cart['totalPrice'] > 50000000:
                payment_method = ["deposit"]
            else:
                payment_method = ['cashondelivery', 'bank_melli', 'bank_mellat', 'bank_saman']

            response_result = {
                "walletAmount": wallet_amount,
                "allowPaymentMethods": payment_method,
            }
            response.status_code = 200
            return {"success": True, "message": response_result, "cart": cart}
        except:
            response.status_code = 404
            return {"success": False, "message": "something went wrong!", "cart": None}


@app.get("/payment_detail_unofficial/", tags=["payment for order"])
def get_payment_unofficial(response: Response, auth_header=Depends(auth_handler.check_current_user_tokens)) -> dict:
    """
        payment and wallet detail for creating payment step
    """
    user, token = auth_header
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        try:
            cart = get_cart(response=response, informal=True, auth_header=auth_header)
            # check if customer select all the shipment methods per stock
            check_shipment_result = check_shipment_per_stock(cart)
            if len(cart['shipment']) != len(check_shipment_result):
                return {"success": False, "message": "!روش ارسال برای همه انبار ها را انتخاب کنید"}
            # TODO add customer request
            rpc.response_len_setter(response_len=1)
            wallet_response = rpc.publish(
                message={
                    "wallet": {
                        "action": "get_wallet_by_customer_id",
                        "body": {
                            "customer_id": user.get("user_id")
                        }
                    }
                },
                headers={'wallet': True}
            ).get("wallet", {})
            wallet_amount = 0
            if wallet_response.get("success"):
                wallet_amount = wallet_response['message'].get('remainingAmount')
            payment_method = ['cashondelivery']
            response_result = {
                "walletAmount": wallet_amount,
                "allowPaymentMethods": payment_method,
            }
            response.status_code = 200
            return {"success": True, "message": response_result, "cart": cart}
        except:
            response.status_code = 404
            return {"success": False, "message": "something went wrong!", "cart": None}


@app.put("/add_shipment", tags=["shipment for order"])
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


@app.put("/wallet", tags=["payment for order"])
def wallet_detail(
        response: Response,
        data: wallet,
        auth_header=Depends(auth_handler.check_current_user_tokens)
):
    user, token_dict = auth_header
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        wallet_response = rpc.publish(
            message={
                "wallet": {
                    "action": "get_wallet_by_customer_id",
                    "body": {
                        "customer_id": user.get("user_id")
                    }
                }
            },
            headers={'wallet': True}
        ).get("wallet", {})
        if wallet_response.get("success"):
            if data.wallet_amount <= wallet_response['message'].get('remainingAmount'):
                rpc.response_len_setter(response_len=1)
                order_response = rpc.publish(
                    message={
                        "cart": {
                            "action": "add_wallet_to_cart",
                            "body": {
                                "user_id": user.get("user_id"),
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
            else:
                raise HTTPException(status_code=500,
                                    detail={"error": "مبلغ وارد شده از موجودی کیف پول کمتر است"})
        else:
            raise HTTPException(status_code=wallet_response.get("status_code", 500),
                                detail={"error": wallet_response.get("error", "wallet service Internal error")})


@app.put("/payment", tags=["payment for order"])
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
                        "user_id": user.get("user_id"),
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

        # check if customer select all the shipment methods per stock
        check_shipment_result = check_shipment_per_stock(cart)
        if len(cart['shipment']) != len(check_shipment_result):
            return {"success": False, "message": "!روش ارسال برای همه انبار ها را انتخاب کنید"}
        elif len(cart['payment']) < 1:
            return {"success": False, "message": "!روش پرداخت را انتخاب کنید"}

        # check quantity

        check_out = check_price_qty(auth_header, cart, response)
        if check_out.get("success"):
            # create order if all data completed
            customer = get_profile_info(auth_header[0])
            create_order = place_order(auth_header, cart, customer)
            if create_order.get("success"):
                if cart['payment'].get("walletAmount") is not None:
                    pass
                if create_order.get("Type") == "pending_payment":
                    send_data = SendData(
                        amount=create_order.get("bank_request").get("amount"),
                        bankName=create_order.get("bank_request").get("bankName"),
                        customerId=create_order.get("bank_request").get("customerId"),
                        serviceName=create_order.get("bank_request").get("serviceName"),
                        orderId=create_order.get("bank_request").get("orderId"),
                    )
                    send_data = convert_case(send_data, "snake")
                    payment_result = get_url(
                        data=send_data,
                        response=Response
                    )
                    response.status_code = create_order.get("status_code")
                    return payment_result
                else:
                    response.status_code = create_order.get("status_code")
                    return create_order.get("message")
            else:
                response.status_code = create_order.get("status_code")
                return create_order.get("message")
        else:
            return check_out.get("message")



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
