from source.message_broker.rabbit_server import RabbitRPC
from starlette.responses import RedirectResponse


def dealership_bank_callback(result, response):
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        get_order_response = rpc.publish(
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
        if get_order_response.get("success"):
            if get_order_response.get('order_object', {}).get('status') == "initial_dealership":
                rpc.response_len_setter(response_len=1)
                if result.get("is_paid"):
                    message = {
                        "order": {
                            "action": "complete_dealership_order_payment",
                            "body": {
                                "payment_data": result
                            }
                        }
                    }
                    order_response = rpc.publish(
                        message=message,
                        headers={'order': True}
                    ).get("order")
                    if order_response.get("success"):
                    #     rpc.response_len_setter(response_len=1)
                    # if order_response['order_object']['status'] == "complete":
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
                            print(credit_response)
                            return RedirectResponse(
                                f"https://aasood.com/payment-result/order/{result.get('service_id')}/")
                        return RedirectResponse(
                            f"https://aasood.com/payment-result/order/{result.get('service_id')}/")
                if not result.get("is_paid"):
                    message = {
                        "order": {
                            "action": "order_bank_callback_cancel",
                            "body": {
                                "payment_data": result
                            }
                        }
                    }
                    cancel_order_response = rpc.publish(
                        message=message,
                        headers={'order': True}
                    ).get("order")
                    if cancel_order_response.get("success"):
                        # rpc.response_len_setter(response_len=1)
                        # dealership_final_response = rpc.publish(
                        #     message={
                        #         "dealership": {
                        #             "action": "insert_order_for_end_user",
                        #             "body": {
                        #                 "order_detail": get_order_response.get("order_object"),
                        #                 "payment_detail": result
                        #             }
                        #         }
                        #     },
                        #     headers={'dealership': True}
                        #     ).get("dealership", {})
                        # if dealership_final_response.get("success"):
                        return RedirectResponse(
                            f"https://aasood.com/payment-result/order/{result.get('service_id')}/")
                    #     return dealership_final_response
                    # return dealership_final_response
                    return RedirectResponse(
                        f"https://aasood.com/payment-result/order/{result.get('service_id')}/")
            # return {"success": False, "message": "سفارش ثبت نشده است"}
            # return RedirectResponse(
            #     f"https://aasood.com/payment-result/order/{result.get('service_id')}/")
        # return get_order_response
        return RedirectResponse(
            f"https://aasood.com/payment-result/order/{result.get('service_id')}/")


# dealership_bank_callback({"payment_id": 300022, "service_id": "300019540", "customer_id": 20008,
#                           "amount": 11000, "bank_name": "mellat", "bank_code": "1011125", "is_paid": True,
#                           "start_payment": 1660069859.52179,
#                           "start_payment_jalali": "1401-05-18 23:00:59", "service": "order",
#                           "kowsar_status": "successful", "return_bank": True,
#                           "send_status": "successful", "status": "واریز با موفقیت انجام شد",
#                           "token": "A8132D79D7416289",
#                           "end_payment": 1660069958.45192, "end_payment_jalali": "1401-05-18 23:02:38",
#                           "payment_log": {"RefId": "A8132D79D7416289", "ResCode": "0", "SaleOrderId": "300022",
#                                           "SaleReferenceId": "220204666585",
#                                           "CardHolderInfo": "F6247BFD28CE23C66AD1755DD026E11CC717A3016E0B17542E01928C609E1DAD",
#                                           "CardHolderPan": "589463******4522", "FinalAmount": "290919000"},
#                           "verify_log": {"ResCode": "0"},
#                           "settle_log": "0", "payment_method": "online_gateway"}, 200)
