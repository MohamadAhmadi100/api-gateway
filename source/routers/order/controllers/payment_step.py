from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Response, Depends
from starlette.exceptions import HTTPException

from source.message_broker.rabbit_server import RabbitRPC
from source.routers.cart.app import get_cart
from source.routers.customer.module.auth import AuthHandler
from source.routers.order.helpers.payment_helper import get_remaining_wallet, informal_to_cart
from source.routers.order.helpers.shipment_helper import check_shipment_per_stock, shipment_detail, is_pos_allowed
from source.routers.order.validators.order import wallet, payment, informal

payment_step_order = APIRouter()

auth_handler = AuthHandler()


@payment_step_order.get("/payment_detail_official/", tags=["payment for order"])
def get_formal_payment(response: Response, auth_header=Depends(auth_handler.check_current_user_tokens)) -> dict:
    """
        payment and wallet detail for creating payment step
    """
    user, token = auth_header
    try:
        cart = get_cart(response=response, auth_header=auth_header)

        # check if customer select all the shipment methods per stock
        check_shipment_result = check_shipment_per_stock(cart)
        if len(cart['shipment']) != len(check_shipment_result):
            return {"success": False, "message": "!روش ارسال برای همه انبار ها را انتخاب کنید"}

        wallet_amount = get_remaining_wallet(user)

        if cart['totalPrice'] > 1000:
            payment_method = [
                {"methodName": "deposit", "methodLabe": "واریز به حساب"}]
        elif cart['totalPrice'] == 0:
            payment_method = []
        else:
            payment_method = [
                              {"methodName": "aiBanking", "methodLabe": "پرداخت انلاین"}]

        # pardakht dar mahal
        allowed_pos = is_pos_allowed(cart)
        if allowed_pos:
            payment_method.append({"methodName": "cashondelivery", "methodLabe": "پرداخت در محل"})

        response_result = {
            "walletAmount": wallet_amount,
            "allowPaymentMethods": payment_method,
        }
        response.status_code = 200
        return {"success": True, "message": response_result, "cart": cart}
    except:
        response.status_code = 404
        return {"success": False, "message": "something went wrong!", "cart": None}


@payment_step_order.get("/payment_detail_informal/", tags=["payment for order"])
def get_informal_payment(response: Response, auth_header=Depends(auth_handler.check_current_user_tokens)) -> dict:
    """
        payment and wallet detail for creating payment step
    """
    user, token = auth_header
    try:
        cart = get_cart(response=response, informal=True, auth_header=auth_header)
        # check if customer select all the shipment methods per stock

        wallet_amount = get_remaining_wallet(user)

        response_result = {
            "walletAmount": wallet_amount,
            "allowPaymentMethods": {
                "cashondelivery": "deposit", "methodLabe": "پرداخت در محل"
            },
        }
        response.status_code = 200
        return {"success": True, "message": response_result, "cart": cart}
    except:
        response.status_code = 404
        return {"success": False, "message": "something went wrong!", "cart": None}


@payment_step_order.put("/wallet/", tags=["payment for order"])
def wallet_detail(
        response: Response,
        data: wallet,
        auth_header=Depends(auth_handler.check_current_user_tokens)
):
    user, token_dict = auth_header
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        cart = get_cart(response=response, auth_header=auth_header)
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
                if data.wallet_amount <= cart.get("totalPrice"):
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
                        get_payment_detail = get_formal_payment(response, auth_header)
                        response.status_code = cart.get("status_code", 200)
                        return {"success": True, "message": "مبلغ از کیف پول شما کسر شد",
                                "payment_detail": get_payment_detail}
                    raise HTTPException(status_code=order_response.get("status_code", 500),
                                        detail={
                                            "error": order_response.get("error", "Order service Internal error")})
                else:
                    raise HTTPException(status_code=500,
                                        detail={"error": "مبلغ وارد شده از مبلغ سفارش بیشتر است"})
            else:
                raise HTTPException(status_code=500,
                                    detail={"error": "مبلغ وارد شده از موجودی کیف پول کمتر است"})
        else:
            raise HTTPException(status_code=wallet_response.get("status_code", 500),
                                detail={"error": wallet_response.get("error", "wallet service Internal error")})


@payment_step_order.put("/payment/", tags=["payment for order"])
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


@payment_step_order.put("/cancel_wallet/", tags=["payment for order"])
def cancele_wallet(response: Response,
                   auth_header=Depends(auth_handler.check_current_user_tokens)):
    user, token_dict = auth_header
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        cart = rpc.publish(
            message={
                "cart": {
                    "action": "remove_wallet",
                    "body": {
                        "user_id": user.get("user_id")
                    }
                }
            },
            headers={'cart': True}
        ).get("cart", {})
        if cart.get("success"):
            get_payment_detail = get_formal_payment(response, auth_header)
            response.status_code = 200
            return {"success": True, "message": "استفاده از کیف پول لغو شد", "payment_detail": get_payment_detail}
        else:
            return {"success": False, "message": "cart internal server error"}


@payment_step_order.get("/payment_informal/", tags=["payment for order"])
def post_informal_payment(data: informal, response: Response,
                          auth_header=Depends(auth_handler.check_current_user_tokens)) -> dict:
    """
        payment and wallet detail for creating payment step
    """
    user, token = auth_header
    try:
        informal_to_cart(user.get("user_id"), informal.national_id)
        response.status_code = 200
        # return {"success": True, "message": response_result, "cart": cart}
    except:
        response.status_code = 404
        return {"success": False, "message": "something went wrong!", "cart": None}
