from fastapi import APIRouter
from typing import Union
from source.message_broker.rabbit_server import RabbitRPC
from source.routers.customer.module.auth import AuthHandler



router = APIRouter()
auth_handler = AuthHandler()


@router.get("/get_list", tags=["get list of requests for warehouse"])
def warehouse_list(storageId: Union[str]):
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        get_list_response = rpc.publish(
            message={
                "dealership": {
                    "action": "get_warehouse_list",
                    "body": {
                        "storage_id": storageId
                    }
                }
            },
            headers={'dealership': True}
        ).get("dealership", {})
        if get_list_response.get("success"):
            return get_list_response
        return get_list_response


@router.get("/get_single_form", tags=["get single form of requests for warehouse"])
def warehouse_single_form(referralNumber: Union[str]):
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        change_status_response = rpc.publish(
            message={
                "dealership": {
                    "action": "change_form_status",
                    "body": {
                        "referral_number": referralNumber
                    }
                }
            },
            headers={'dealership': True}
        ).get("dealership", {})
        if change_status_response.get("success"):
            get_form_response = rpc.publish(
                message={
                    "dealership": {
                        "action": "get_warehouse_single_form",
                        "body": {
                            "referral_number": referralNumber
                        }
                    }
                },
                headers={'dealership': True}
            ).get("dealership", {})
            if get_form_response.get("success"):
                return get_form_response
            return get_form_response
        return change_status_response