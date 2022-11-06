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
            if get_order_response['order_object']['status'] == "dealership_initial":
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
                            rpc.response_len_setter(response_len=1)
                        # if order_response['order_object']['status'] == "complete_dealership":
                            reduce_inventory = rpc.publish(
                                message={
                                    "dealership": {
                                        "action": "reduce_inventory",
                                        "body": {
                                            "order_detail": get_order_response.get("order_object"),
                                            # "payment_detail": payment_detail
                                        }
                                    }
                                },
                                headers={'dealership': True}
                            ).get("dealership", {})
                            if reduce_inventory.get("success"):
                                rpc.response_len_setter(response_len=1)
                                dealership_response = rpc.publish(
                                    message={
                                        "dealership": {
                                            "action": "insert_order_for_end_user",
                                            "body": {
                                                "order_detail": get_order_response.get("order_object"),
                                                "payment_detail": result
                                            }
                                        }
                                    },
                                    headers={'dealership': True}
                                ).get("dealership", {})
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
            return RedirectResponse(
                f"https://aasood.com/payment-result/order/{result.get('service_id')}/")
        # return get_order_response
        return RedirectResponse(
            f"https://aasood.com/payment-result/order/{result.get('service_id')}/")



#
# print(dealership_bank_callback({
#     "payment_id" : 303965,
#     "service_id" : 300010443,
#     "customer_id" : 20003,
#     "amount" : 688000,
#     "bank_name" : "mellat",
#     "bank_code" : "1011125",
#     "is_paid" : True,
#     "start_payment" : 1663136268.27697,
#     "start_payment_jalali" : "1401-06-23 10:47:48",
#     "service" : "order",
#     "kowsar_status" : "successful",
#     "return_bank" : True,
#     "send_status" : "successful",
#     "status" : "واریز با موفقیت انجام شد",
#     "token" : "3247184508A5211A",
#     "end_payment" : 1663136310.24705,
#     "end_payment_jalali" : "1401-06-23 10:48:30",
#     "payment_log" : {
#         "RefId" : "3247184508A5211A",
#         "ResCode" : "0",
#         "SaleOrderId" : "303965",
#         "SaleReferenceId" : "222800917074",
#         "CardHolderInfo" : "12ECB0F339C5528069DD48C8421CC66B1988551BDD9E14574A948FEBC514D516",
#         "CardHolderPan" : "585983****2397",
#         "FinalAmount" : "237580000"
#     },
#     "verify_log" : {
#         "ResCode" : "0"
#     },
#     "settle_log" : "0"
# }, 200))