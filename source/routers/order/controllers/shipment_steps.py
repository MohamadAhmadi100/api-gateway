from fastapi import APIRouter
from fastapi import HTTPException, Response, Depends
from starlette.exceptions import HTTPException

from source.message_broker.rabbit_server import RabbitRPC
from source.routers.cart.app import get_cart
from source.routers.customer.module.auth import AuthHandler
from source.routers.order.helpers.shipment_helper import shipment_detail
from source.routers.shipment.validators.shipment_per_stock import PerStock

shipment_step = APIRouter()

auth_handler = AuthHandler()


@shipment_step.get("/shipment_detail/", tags=["shipment for order"])
def get_shipment(response: Response, auth_header=Depends(auth_handler.check_current_user_tokens)) -> dict:
    """
        all process for creating an order is here
    """
    response_result = shipment_detail(auth_header, response)
    if response_result.get("success"):
        with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
            rpc.response_len_setter(response_len=1)
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
            response.status_code = response_result.get("status_code")
            return {"success": True, "message": response_result.get("message")}
    else:
        raise HTTPException(status_code=500,
                            detail={"success": False, "message": response_result.get("message")})


@shipment_step.put("/add_shipment/", tags=["shipment for order"])
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
                        "data": data.dict()
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
