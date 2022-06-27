from typing import Union

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Query
from fastapi import Response, Depends
from starlette.exceptions import HTTPException

from source.message_broker.rabbit_server import RabbitRPC
from source.routers.customer.module.auth import AuthHandler
from source.routers.order.helpers.final_helper import remove_from_reserve_order_items
from source.routers.order.validators.order import cancel

edit_order = APIRouter()

auth_handler = AuthHandler()


@edit_order.put("/cancel_order/", tags=["Edit order"])
def cancel_order(response: Response,
                 data: cancel,
                 auth_header=Depends(auth_handler.check_current_user_tokens)):
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        order_result = rpc.publish(
            message={
                "order": {
                    "action": "cancel_order_by_customer",
                    "body": {
                        "order_number": data.orderNumber
                    }
                }
            },
            headers={'order': True}
        ).get("order")
        if order_result.get("success"):
            reserve_action = remove_from_reserve_order_items(order_object=order_result.get("order_object"))
            if reserve_action.get("success"):
                response.status_code = order_result.get("status_code")
                return {"success": True, "message": order_result.get("message")}
            else:
                return {"success": False, "message": "رزرو تغییر نکرد"}
        else:
            return order_result
