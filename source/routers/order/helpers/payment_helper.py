from source.message_broker.rabbit_server import RabbitRPC


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