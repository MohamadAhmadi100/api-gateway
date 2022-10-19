from fastapi import APIRouter, Depends, Query
from typing import Optional, Union
from source.message_broker.rabbit_server import RabbitRPC
from source.routers.customer.module.auth import AuthHandler



router = APIRouter()
auth_handler = AuthHandler()


@router.get("/get_dealership_inventory", tags=["get list of products of dealership"])
def products_list(
    imei: Optional[str]=Query(default=None),
    product_name: Optional[str]=Query(default=None),
    auth_header=Depends(auth_handler.check_current_user_tokens),
):
    user, token = auth_header
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        get_list_response = rpc.publish(
            message={
                "dealership": {
                    "action": "get_dealership_inventory",
                    "body": {
                        "customer_id": str(user.get("user_id")),
                        "imei": imei,
                        "product_name": product_name

                    }
                }
            },
            headers={'dealership': True}
        ).get("dealership", {})
        if get_list_response.get("success"):
            return get_list_response
        return get_list_response


@router.get("/get_initial", tags=["get initial page"])
def initial(
    auth_header=Depends(auth_handler.check_current_user_tokens)
):
    user, token = auth_header
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        get_initial= rpc.publish(
            message={
                "dealership": {
                    "action": "get_initial",
                    "body": {
                        "customer_id": str(user.get("user_id"))
                    }
                }
            },
            headers={'dealership': True}
        ).get("dealership", {})
        if get_initial.get("success"):
            return get_initial
        return get_initial


@router.get("/get_sell_forms", tags=["get all sell forms that are added by dealership"])
def get_sell_forms(
    auth_header=Depends(auth_handler.check_current_user_tokens)
):
    user, token = auth_header
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        response= rpc.publish(
            message={
                "dealership": {
                    "action": "get_sell_forms",
                    "body": {
                        "dealership_id": str(user.get("user_id"))
                    }
                }
            },
            headers={'dealership': True}
        ).get("dealership", {})
        if response.get("success"):
            return response
        return response


