from fastapi import HTTPException
from starlette.exceptions import HTTPException

from source.message_broker.rabbit_server import RabbitRPC
from source.routers.wallet.app import reserve_wallet, complete_order_wallet


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


def unofficial_to_cart(user):
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        cart_response = rpc.publish(
            message={
                "cart": {
                    "action": "add_official_unofficial",
                    "body": {
                        "user_id": user.get("user_id")
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
    if wallet_amount > cart['grandPrice']:
        wallet_amount = cart['grandPrice']
    data_reserve_wallet = {
        "amount": wallet_amount,
        "orderNumber": palceorder_result['orderNumber'],
        "ActionType": "auto",
        "balance": "consume",
        "type": "order"
    }

    if palceorder_result['totalPrice'] > 0:
        wallet_response = reserve_wallet(data=data_reserve_wallet, response=response,
                                         auth_header=auth_header)
        if not wallet_response.get("success"):
            raise HTTPException(status_code=wallet_response.get("status_code", 500),
                                detail={"error": "wallet not response"})

    elif palceorder_result['totalPrice'] == 0:
        data_reserve_wallet['status'] = "success"
        wallet_response = complete_order_wallet(order_data=data_reserve_wallet, response=response,
                                                auth_header=auth_header)
        if not wallet_response.get("success"):
            raise HTTPException(status_code=wallet_response.get("status_code", 500),
                                detail={"error": "wallet not response"})
