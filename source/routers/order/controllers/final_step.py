from fastapi import APIRouter
from fastapi import Response, Depends

from source.helpers.case_converter import convert_case
from source.message_broker.rabbit_server import RabbitRPC
from source.routers.cart.app import get_cart
from source.routers.customer.helpers.profile_view import get_profile_info
from source.routers.customer.module.auth import AuthHandler
from source.routers.order.helpers.check_out import check_price_qty
from source.routers.order.helpers.final_helper import place_order, reserve_order_items, \
    delete_order_reserving_fail, add_final_flag_to_cart
from source.routers.order.helpers.payment_helper import wallet_final_consume
from source.routers.order.helpers.shipment_helper import check_shipment_per_stock
from source.routers.order.validators.order import final
from source.routers.payment.controllers.bank_controller import get_url
from source.routers.payment.validators.payment import SendData
from source.routers.order.helpers.log import log_decorator

final_step_order = APIRouter()

auth_handler = AuthHandler()
rpc = RabbitRPC(exchange_name='headers_exchange', timeout=1000)


@final_step_order.put("/final/", tags=["final steps and create order"])
@log_decorator
def final_order(
        response: Response,
        data: final,
        auth_header=Depends(auth_handler.check_current_user_tokens)
) -> dict:
    user, token_dict = auth_header
    customer_type = user.get("customer_type")[0]
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        cart = get_cart(response=response, auth_header=auth_header)
        check_shipment_result = check_shipment_per_stock(cart)
        if len(cart['shipment']) != len(check_shipment_result):
            response.status_code = 400
            return {"success": False, "message": "!روش ارسال برای همه انبار ها را انتخاب کنید"}
        elif len(cart['payment']) < 1:
            response.status_code = 400
            return {"success": False, "message": "!روش پرداخت را انتخاب کنید"}

        # check quantity
        check_out = check_price_qty(auth_header, cart, response)
        if check_out.get("success"):
            # create order if all data completed
            customer = get_profile_info(auth_header[0])
            place_order_result = place_order(auth_header, cart, customer, data.device_type)
            if place_order_result.get("success"):
                result_reserve = reserve_order_items(place_order_result.get("order_object"))
                if result_reserve.get("success"):
                    if cart['payment'].get("walletAmount") is not None:
                        wallet_final_consume(place_order_result, cart, auth_header, response)

                    if place_order_result.get("Type") == "pending_payment":
                        add_final_flag_to_cart(auth_header)
                        send_data = SendData(
                            amount=int(place_order_result.get("bank_request").get("amount")) * 10,
                            customerId=int(place_order_result.get("bank_request").get("customerId")),
                            serviceName=place_order_result.get("bank_request").get("serviceName"),
                            serviceId=str(place_order_result.get("bank_request").get('serviceId')),
                            customerType=customer_type
                        )
                        send_data = convert_case(send_data, "snake")
                        payment_result = get_url(
                            data=send_data,
                            response=response
                        )
                        if payment_result.get("success"):
                            response.status_code = payment_result.get("status_code")
                            return {"success": True, "Type": "pending_payment",
                                    "paymentResult": payment_result.get("message")}
                        else:
                            rpc.response_len_setter(response_len=1)
                            rpc.publish(
                                message={
                                    "order": {
                                        "action": "order_delete",
                                        "body": {
                                            "order_data": place_order_result.get("order_object")
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
                                            "order": place_order_result.get("order_object")
                                        }
                                    }
                                },
                                headers={"product": True}
                            ).get("product")
                            payment_result['gateway_message'] = "خطا در برقراری ارتباط با بانک"
                            return {"success": False, "paymentResult": payment_result.get("error")}
                    else:
                        rpc.response_len_setter(response_len=1)
                        rpc.publish(
                            message={
                                "order": {
                                    "action": "send_place_order_sms",
                                    "body": {
                                        "phone_number": place_order_result['order_object']['customer']['mobile'],
                                        "first_name":
                                            place_order_result['order_object']['customer']['fullName'].split(" ")[0],
                                        "last_name":
                                            place_order_result['order_object']['customer']['fullName'].split(" ")[1],
                                        "order_number": place_order_result['order_object']['orderNumber']
                                    }
                                }
                            },
                            headers={'order': True}
                        )
                        rpc.response_len_setter(response_len=1)
                        rpc.publish(
                            message={
                                "cart": {
                                    "action": "delete_cart",
                                    "body": {
                                        "user_id": auth_header[0].get("user_id")
                                    }
                                }
                            },
                            headers={'cart': True}
                        )
                        response.status_code = place_order_result.get("status_code")
                        return place_order_result
                else:
                    delete_order_reserving_fail(place_order_result.get("order_object"))
                    check_out = check_price_qty(auth_header, cart, response)
                    response.status_code = 400
                    check_out['gateway_message'] = "خطا در رزرو کالا"
                    return {"success": False, "message": check_out.get("message")}
            else:
                rpc.response_len_setter(response_len=1)
                rpc.publish(
                    message={
                        "cart": {
                            "action": "remove_cart",
                            "body": {
                                "user_id": auth_header[0].get("user_id"),
                            }
                        }
                    },
                    headers={'cart': True}
                )
                response.status_code = place_order_result.get("status_code", 400)
                place_order_result['gateway_error'] = "خطا در ثبت سفارش"
                return place_order_result
        else:
            rpc.response_len_setter(response_len=1)
            rpc.publish(
                message={
                    "cart": {
                        "action": "remove_cart",
                        "body": {
                            "user_id": auth_header[0].get("user_id"),
                        }
                    }
                },
                headers={'cart': True}
            )

            response.status_code = 400
            return {"success": False, "error": check_out.get("message")}