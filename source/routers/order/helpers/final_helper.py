from fastapi.responses import RedirectResponse

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
                wallet_amount = order_get_response['order_object']['payment'].get('paymentMethod')[0].get(
                    "walletConsume")
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
                # send sms
                rpc.response_len_setter(response_len=1)
                rpc.publish(
                    message={
                        "order": {
                            "action": "send_place_order_sms",
                            "body": {
                                "phone_number": order_get_response['order_object']['customer']['mobile'],
                                "first_name":
                                    order_get_response['order_object']['customer']['fullName'].split(" ")[0],
                                "last_name":
                                    order_get_response['order_object']['customer']['fullName'].split(" ")[1],
                                "order_number": order_get_response['order_object']['orderNumber'],
                                "customer_type": order_get_response['order_object']['customer']['type']
                            }
                        }
                    },
                    headers={'order': True}
                )

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
                if order_get_response['order_object']['customer']['type'] == "B2B":
                    return RedirectResponse(
                        f"https://aasood.com/payment-result/order/{result.get('service_id')}")
                elif order_get_response['order_object']['customer']['type'] == "B2C":
                    return RedirectResponse(
                        f"https://rakiano.com/payment-result/order/{result.get('service_id')}")
            else:
                rpc.response_len_setter(response_len=1)
                rpc.publish(
                    message={
                        "order": {
                            "action": "send_cancel_order_sms",
                            "body": {
                                "phone_number": order_get_response['order_object']['customer']['mobile'],
                                "first_name":
                                    order_get_response['order_object']['customer']['fullName'].split(" ")[0],
                                "last_name":
                                    order_get_response['order_object']['customer']['fullName'].split(" ")[1],
                                "order_number": order_get_response['order_object']['orderNumber'],
                                "customer_type": order_get_response['order_object']['customer']['type']
                            }
                        }
                    },
                    headers={'order': True}
                )
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

                if order_get_response['order_object']['customer']['type'] == "B2B":
                    return RedirectResponse(
                        f"https://aasood.com/payment-result/order/{result.get('service_id')}")
                elif order_get_response['order_object']['customer']['type'] == "B2C":
                    return RedirectResponse(
                        f"https://rakiano.com/payment-result/order/{result.get('service_id')}")
        else:
            if order_get_response['order_object']['customer']['type'] == "B2B":
                return RedirectResponse(
                    f"https://aasood.com/payment-result/order/{result.get('service_id')}")
            elif order_get_response['order_object']['customer']['type'] == "B2C":
                return RedirectResponse(
                    f"https://rakiano.com/payment-result/order/{result.get('service_id')}")


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


def place_order(auth_header, cart, customer, device_type):
    user, token_dict = auth_header
    # check if all will have response(timeout)
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        result = dict()
        result['cart'] = cart
        result['user_info'] = user
        result['customer'] = customer
        result['device_type'] = device_type
        rpc.response_len_setter(response_len=1)
        warehouse_result = rpc.publish(
            message={
                "product": {
                    "action": "all_warehouses",
                    "body": {
                    }
                }
            },
            headers={"product": True}
        ).get("product")['warehouses']
        result['warehouse_details'] = warehouse_result

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
            return {"success": False, "message": "خطا در ثبت سفارش. لطفا با پشتیبانی تماس بگیرید",
                    "error": result.get("error"), "status_code": 400}


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
