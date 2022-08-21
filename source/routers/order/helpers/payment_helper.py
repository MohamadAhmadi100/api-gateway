from fastapi import HTTPException
from starlette.exceptions import HTTPException

from source.message_broker.rabbit_server import RabbitRPC
from source.routers.wallet.controllers.other_controllers import reserve_wallet, complete_order_wallet


def get_remaining_wallet(user):
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
        wallet_amount = 0
        if wallet_response.get("success"):
            wallet_amount = wallet_response['message'].get('remainingAmount')
        return wallet_amount


def informal_to_cart(user, national_id):
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        result = rpc.publish(
            message={
                "customer": {
                    "action": "get_informal",
                    "body": {
                        "data": {
                            "customer_mobile_number": user.get("phone_number"),
                            "informal_national_id": national_id
                        }
                    }
                }
            },
            headers={'customer': True}
        )
        customer_detail = "asdasdasd"
        rpc.response_len_setter(response_len=1)
        cart_response = rpc.publish(
            message={
                "cart": {
                    "action": "add_official_unofficial",
                    "body": {
                        "user_id": user.get("user_id"),
                        "customer_detail": customer_detail
                    }
                }
            },
            headers={'cart': True}
        ).get("cart", {})
        if cart_response.get("success"):
            return "اطلاعات با موفقیت در کارت ثبت شد"
        else:
            return None


def wallet_final_consume(palceorder_result, cart, auth_header, response):
    wallet_amount = cart['payment'].get("walletAmount")
    data_reserve_wallet = {
        "amount": wallet_amount,
        "order_number": palceorder_result['orderNumber'],
        "action_type": "auto",
        "balance": "consume",
        "type": "order"
    }

    if palceorder_result['totalPrice'] > 0:
        wallet_response = reserve_wallet(data=data_reserve_wallet, response=response,
                                         auth_header=auth_header)
        if not wallet_response.get("success"):
            raise HTTPException(status_code=wallet_response.get("status_code", 500),
                                detail={"error": "wallet not response"})

    elif palceorder_result['totalPrice'] == 0 or palceorder_result.get("Type") == "pos":
        data_reserve_wallet['status'] = "success"
        wallet_response = complete_order_wallet(order_data=data_reserve_wallet, response=response,
                                                auth_header=auth_header)
        if not wallet_response.get("success"):
            raise HTTPException(status_code=wallet_response.get("status_code", 500),
                                detail={"error": "wallet not response"})


def wallet_payment_consume(payment_detail, cart):
    wallet_amount = cart['payment'].get("walletAmount")
    if payment_detail.get("is_paid"):
        data_reserve_wallet = {"amount": wallet_amount, "order_number": payment_detail['service_id'],
                               "action_type": "auto",
                               "balance": "consume", "type": "order", 'status': "success",
                               "customer_id": payment_detail.get("customer_id")}

    else:
        data_reserve_wallet = {"amount": wallet_amount, "order_number": payment_detail['service_id'],
                               "action_type": "auto",
                               "balance": "charge", "type": "order", 'status': "failed",
                               "customer_id": payment_detail.get("customer_id")}

    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        # send refresh and access token to front in header
        rpc.response_len_setter(response_len=1)
        wallet_response = rpc.publish(
            message={
                "wallet": {
                    "action": "result_checkout",
                    "body": {
                        "data": data_reserve_wallet
                    }
                }
            },
            headers={'wallet': True}
        ).get("wallet", {})
        return wallet_response


def charge_wallet_edit_order(order_number, user, amount):
    last_data = {
        "staff_name": None,
        "amount": amount,
        "staff_id": None,
        "balance": "charge",
        "action_type": "auto",
        "type": "customerCharge",
        "reason": {"orderNumber": order_number, "reason": "cancel order"},
        "customer_id": user.get("user_id")
    }
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        wallet_response = rpc.publish(
            message={
                "wallet": {
                    "action": "update_wallet",
                    "body": {
                        "data": last_data
                    }
                }
            },
            headers={'wallet': True}
        ).get("wallet", {})
        return wallet_response
