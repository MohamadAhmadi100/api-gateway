from typing import Union

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Query
from fastapi import Response, Depends
from starlette.exceptions import HTTPException

from source.message_broker.rabbit_server import RabbitRPC
from source.routers.customer.module.auth import AuthHandler
from source.routers.order.helpers.final_helper import remove_from_reserve_order_items
from source.routers.order.helpers.payment_helper import charge_wallet_edit_order
from source.routers.order.validators.order import cancel, edit_order_validator

edit_order = APIRouter()

auth_handler = AuthHandler()


@edit_order.put("/cancel_order/", tags=["Edit order"])
def cancel_order(response: Response,
                 data: cancel,
                 auth_header=Depends(auth_handler.check_current_user_tokens)):
    user, token_dict = auth_header
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        get_order_result = rpc.publish(
            message={
                "order": {
                    "action": "get_one_order",
                    "body": {
                        "order_id": data.orderNumber
                    }
                }
            },
            headers={'order': True}
        ).get("order")
        allowed_statuses = ["processing", "pending_payment", "pending_accounting", "pos"]
        order_object = get_order_result.get("order_object")
        if order_object['status'] not in allowed_statuses:
            response.status_code = 400
            return {"success": False, "message": "سفارش قابل تغییر وضعیت نیست"}
        reserve_action = remove_from_reserve_order_items(order_object=order_object)
        if reserve_action.get("success"):
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
                if order_result['wallet_charge'] == 0:
                    return {"success": True, "message": "سفارش با موفقیت لغو شد"}
                else:
                    wallet_result = charge_wallet_edit_order(data.orderNumber, user, order_result['wallet_charge'])
                    if wallet_result:
                        response.status_code = order_result.get("status_code")
                        return {"success": True, "message": order_result.get("message")}
                    else:
                        return {"success": True, "message": "سفارش با موفقیت لغو شد ولی کیف پول شما شارژ نشد. با ادمین تماس بگیرید"}

            else:
                response.status_code = 400
                return order_result
        else:
            response.status_code = 400
            return {"success": False, "message": "عملیات ناموفق بود"}


@edit_order.put("/edit_order/", tags=["Edit order"])
def edit_order_items(response: Response,
                     data: edit_order_validator,
                     auth_header=Depends(auth_handler.check_current_user_tokens)):
    user, auth_head = auth_header
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=2)
        order_result = rpc.publish(
            message={
                "order": {
                    "action": "edit_order",
                    "body": {
                        "order_number": data.orderNumber,
                        "edited_object": data.edit_list
                    }
                }, "quantity": {
                    "action": "remove_reserve_edit",
                    "body": {
                        "order_number": data.orderNumber,
                        "edited_object": data.edit_list,
                        "customer_id": data.customerId,
                        "customer_name": data.customerFullName,
                        "customer_type": data.customerType
                    }
                }},
            headers={'order': True, "quantity": True}
        )
        order = order_result.get("order", {})
        quantity = order_result.get("quantity", {})
        if order.get("success") and quantity.get("success"):
            wallet_result = charge_wallet_edit_order(data.orderNumber, user, order.get('wallet_charge'))
            if wallet_result.get("success"):
                response.status_code = 200
                return {"succeess": True, "message": "سفارش با موفقیت ویرایش شد"}
            else:
                response.status_code = 400
                return {"succeess": True, "message": "سفارش با موفقیت ویرایش شد ولی کیف پول شارژ نشد. با ادمین تماس بگیرید"}
        elif not order.get("success"):
            response.status_code = 400
            return {"succeess": False, "message": "سفارش با مشکل موجه شد"}
        elif not quantity.get("success"):
            response.status_code = 400
            return {"succeess": False, "message": "رزرو با مشکل موحه شد"}
