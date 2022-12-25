from fastapi import Depends, APIRouter, Query

from source.helpers.case_converter import convert_case
from source.message_broker.rabbit_server import RabbitRPC
from source.routers.customer.helpers.profile_view import get_profile_info
from source.routers.customer.module.auth import AuthHandler
from source.routers.dealership.validators.register_sell_request import SellRequest
from source.routers.uis.app import create_link
from source.routers.uis.validators.uis import Uis

router = APIRouter()
auth_handler = AuthHandler()


@router.put("/complete_dealership_sell_request", tags=["Complete payment"])
def sell_request(order_id: str = Query(..., alias="orderId"),
                 auth_header=Depends(auth_handler.check_current_user_tokens)):
    user, token = auth_header
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        get_order_response = rpc.publish(
            message={
                "order": {
                    "action": "get_one_order",
                    "body": {
                        "order_id": order_id
                    }
                }
            },
            headers={'order': True}
        ).get("order")
        if get_order_response.get("success"):
            rpc.response_len_setter(response_len=1)
            order_response = rpc.publish(
                message={
                    "order": {
                        "action": "complete_dealership",
                        "body": {
                            "order_number": order_id,
                        }
                    }
                },
                headers={'order': True}
            ).get("order", {})
            if order_response.get("success"):
                reduce_inventory = rpc.publish(
                    message={
                        "dealership": {
                            "action": "reduce_inventory",
                            "body": {
                                "order_detail": get_order_response.get("order_object"),
                            }
                        }
                    },
                    headers={'dealership': True}
                ).get("dealership", {})
                rpc.response_len_setter(response_len=1)
                price_response = rpc.publish(
                    message={
                        "dealership": {
                            "action": "products_b2b_price",
                            "body": {
                                "order": get_order_response.get("order_object"),
                            }
                        }
                    },
                    headers={'dealership': True}
                ).get("dealership", {})
                print(price_response)
                if reduce_inventory.get("success"):
                    rpc.response_len_setter(response_len=1)
                    credit_response = rpc.publish(
                        message={
                            "credit": {
                                "action": "insert_accounting_record",
                                "body": {
                                    "order_detail": price_response.get("message"),
                                }
                            }
                        },
                        headers={'credit': True}
                    ).get("credit", {})
                    return credit_response
                return reduce_inventory
            return order_response
        return get_order_response









