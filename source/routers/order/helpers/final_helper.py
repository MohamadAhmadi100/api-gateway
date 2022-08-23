from source.message_broker.rabbit_server import RabbitRPC


def handle_order_bank_callback(result, response):
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        order_get_response = rpc.publish(
            message={
                "order": {
                    "action": "get_one_order",
                    "body": {
                        "order_id": result.get("service_id")
                    }
                }
            },
            headers={'order': True}
        ).get("order")
        if order_get_response['order_object']['status'] == "pending_payment":
            if order_get_response.get("order_object") is not None:
                wallet_amount = order_get_response['order_object']['payment'].get('paymentMethod')[0].get("walletConsume")
                # consume wallet
                if wallet_amount is not None:
                    if result.get("is_paid"):
                        data_reserve_wallet = {"amount": wallet_amount, "order_number": result['service_id'],
                                               "action_type": "auto",
                                               "balance": "consume", "type": "order", 'status': "success",
                                               "customer_id": result.get("customer_id")}

                    else:
                        data_reserve_wallet = {"amount": wallet_amount, "order_number": result['service_id'],
                                               "action_type": "auto",
                                               "balance": "charge", "type": "order", 'status': "failed",
                                               "customer_id": result.get("customer_id")}

                    # send refresh and access token to front in header
                    rpc.response_len_setter(response_len=1)
                    wallet_result = rpc.publish(
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

            if result['is_paid']:
                rpc.response_len_setter(response_len=2)
                car_order_result = rpc.publish(
                    message={
                        "order": {
                            "action": "order_bank_callback_processing",
                            "body": {
                                "payment_data": result
                            }
                        },
                        "cart": {
                            "action": "delete_cart",
                            "body": {
                                "user_id": result.get("customer_id")
                            }
                        }

                    },
                    headers={'order': True, "cart": True}
                )

                # response.status_code = 200
                return {"result": True, "service_id": result.get("service_id")}

            else:
                rpc.response_len_setter(response_len=1)
                rpc.publish(
                    message={
                        "order": {
                            "action": "order_bank_callback_cancel",
                            "body": {
                                "payment_data": result
                            }
                        }
                    },
                    headers={'order': True}
                ).get("order")

                rpc.response_len_setter(response_len=1)
                rpc.publish(
                    message={
                        "product": {
                            "action": "remove_from_reserve",
                            "body": {
                                "order": order_get_response.get("order_object")
                            }
                        }
                    },
                    headers={"product": True}
                ).get("product")
                rpc.response_len_setter(response_len=1)
                rpc.publish(
                    message={
                        "cart": {
                            "action": "remove_cart_bank_callback",
                            "body": {
                                "user_id": result.get("customer_id")
                            }
                        }
                    },
                    headers={"cart": True}
                )
                response.status_code = 200
                return {"result": False, "service_id": result.get("service_id")}
        else:
            return {"result": False, "service_id": result.get("service_id")}

def reserve_order_items(order_object):
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        order_response = rpc.publish(
            message={
                "product": {
                    "action": "add_to_reserve",
                    "body": {
                        "order": order_object,
                    }
                }
            },
            headers={'product': True}
        ).get("product", {})
        return order_response


def remove_from_reserve_order_items(order_object):
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        order_response = rpc.publish(
            message={
                "product": {
                    "action": "remove_from_reserve",
                    "body": {
                        "order": order_object,
                    }
                }
            },
            headers={'product': True}
        ).get("product", {})
        return order_response


def delete_order_reserving_fail(order_object):
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        order_response = rpc.publish(
            message={
                "order": {
                    "action": "order_delete",
                    "body": {
                        "order_data": order_object,
                    }
                }
            },
            headers={'order': True}
        ).get("order", {})
        return order_response


def place_order(auth_header, cart, customer):
    user, token_dict = auth_header
    # check if all will have response(timeout)
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        result = dict()
        result['cart'] = cart
        result['user_info'] = user
        result['customer'] = customer

        rpc.response_len_setter(response_len=1)
        result_to_order = rpc.publish(
            message={
                "order": {
                    "action": "place_order",
                    "body": {
                        "order_data": result,
                    }
                }
            },
            headers={'order': True}
        ).get("order")
        if result_to_order.get("success"):
            return result_to_order
        else:
            return {"success": False, "message": "something went wrong!"}


def add_final_flag_to_cart(auth_header):
    user, token_dict = auth_header
    # check if all will have response(timeout)
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        result_to_order = rpc.publish(
            message={
                "cart": {
                    "action": "final_flag",
                    "body": {
                        "user_id": user.get("user_id"),
                    }
                }
            },
            headers={'cart': True}
        ).get("cart")
        if result_to_order.get("success"):
            return result_to_order
        else:
            return {"success": False, "message": "something went wrong!"}

handle_order_bank_callback({
    "payment_id" : 300103,
    "service_id" : "300001882",
    "customer_id" : 11284,
    "amount" : 185797560,
    "bank_name" : "mellat",
    "bank_code" : "1011125",
    "is_paid" : False,
    "start_payment" : 1660142963.41641,
    "start_payment_jalali" : "1401-05-19 19:19:23",
    "service" : "order",
    "kowsar_status" : {},
    "return_bank" : True,
    "send_status" : "sent",
    "status" : "کاربر از بانک به ضفحه آسود بازگشت",
    "token" : "F482517F5D252A56",
    "end_payment" : 1660143026.61919,
    "end_payment_jalali" : "1401-05-19 19:20:26",
    "payment_log" : {
        "RefId" : "F482517F5D252A56",
        "ResCode" : "0",
        "SaleOrderId" : "300103",
        "SaleReferenceId" : "220273384971",
        "CardHolderInfo" : "7BF381E437B6D995486D3720D5263ACD0110DDC34D9701D24FE10C49A5D8D1F3",
        "CardHolderPan" : "610433****6064",
        "FinalAmount" : "185797560"
    },
    "verify_log" : {
        "ResCode" : "0"
    },
    "settle_log" : "0"
},200)