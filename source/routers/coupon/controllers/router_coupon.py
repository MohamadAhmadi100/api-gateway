import json

from fastapi import APIRouter, Depends, Response, HTTPException
from source.message_broker.rabbit_server import RabbitRPC
from source.routers.customer.module.auth import AuthHandler
from source.routers.coupon.validators.coupon import Coupon
from source.routers.cart.app import get_cart

router_coupon = APIRouter(
    prefix="/coupon",
    tags=["coupon"]
)
auth_handler = AuthHandler()


@router_coupon.post("/add")
def add_coupon_to_cart(
        data: Coupon,
        response: Response,
        auth_header=Depends(auth_handler.check_current_user_tokens)
):
    user_data, header = auth_header
    cart = get_cart(response=response, auth_header=auth_header)
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        coupon_result = rpc.publish(
            message={
                "coupon": {
                    "action": "check_coupon",
                    "body": {
                        "customer_id": user_data.get("user_id"),
                        "token": data.token,
                        "cart": cart
                    }
                }
            },
            headers={'coupon': True}
        )
    coupon_result = coupon_result.get("coupon", {})
    if not coupon_result.get("success"):
        raise HTTPException(
            status_code=coupon_result.get("status_code", 500),
            detail={"error": coupon_result.get("error", "Something went wrong")}
        )
    if coupon := coupon_result.get("coupon"):
        with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
            rpc.response_len_setter(response_len=1)
            result = rpc.publish(
                message={
                    "cart": {
                        "action": "add_coupon_to_cart",
                        "body": {
                            "user_id": user_data.get("user_id"),
                            "coupon": coupon
                        }
                    }
                },
                headers={'cart': True}
            )
            cart_result = result.get("cart", {})
            if not cart_result.get("success"):
                raise HTTPException(status_code=cart_result.get("status_code", 500),
                                    detail={"error": cart_result.get("error", "Something went wrong")})

    sub_dict = {
        "user_id": user_data.get('user_id'),
        "customer_type": user_data.get('customer_type'),
        "phone_number": user_data.get('phone_number'),
    }
    response.headers["accessToken"] = auth_handler.encode_refresh_token(sub_dict)
    response.headers["refresh_token"] = auth_handler.encode_access_token(sub_dict)
    response.status_code = coupon_result.get("status_code", 200)
    return {"message": coupon_result.get("message", {}), "data": coupon_result.get("data", {})}
