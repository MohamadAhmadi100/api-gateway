from fastapi import Depends, APIRouter
from source.message_broker.rabbit_server import RabbitRPC
from source.routers.customer.module.auth import AuthHandler
from source.routers.dealership.validators.register_request import RequestGoods


router = APIRouter()
auth_handler = AuthHandler()


@router.post("/create_request_goods", tags=["register forms"])
def create_request(data: RequestGoods,
                   auth_header=Depends(auth_handler.check_current_user_tokens)):
    user, token = auth_header
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        customer_response = rpc.publish(
            message={
                "customer": {
                    "action": "get_profile",
                    "body": {
                        "customer_phone_number": user
                    }
                }
            },
            headers={'customer': True}
        ).get("customer", {})
        if customer_response.get("success"):
            for item in customer_response.get("message"):
                if item.get("name") == "customerFirstName":
                    customer_first_name = item.get("value")
                if item.get("name") == "customerLastName":
                    customer_last_name = item.get("value")
            dealership_response = rpc.publish(
                message={
                    "dealership": {
                        "action": "customer_products_value",
                        "body": {
                            "customer_id": user.get("user_id"),
                        }
                    }
                },
                headers={'dealership': True}
            ).get("dealership", {})
            if dealership_response.get("success"):
                rpc.response_len_setter(response_len=1)
                check_credit = rpc.publish(
                    message={
                        "credit": {
                            "action": "get_remaining_credit",
                            "body": {
                                "customer_id": user.get("user_id"),
                                "products_value": dealership_response.get("message")
                            }
                        }
                    },
                    headers={'credit': True}
                ).get("credit", {})
                if check_credit.get("success"):
                    print(check_credit)

                    rpc.response_len_setter(response_len=1)
                    dict_data = data.dict()
                    compare_digits_response = rpc.publish(
                        message={
                            "dealership": {
                                "action": "check_credit_state",
                                "body": {
                                    "credit": check_credit.get("message").get("remainingCredit"),
                                    "products": dict_data.get("products")
                                }
                            }
                        },
                        headers={'dealership': True}
                    ).get("dealership", {})
                    if compare_digits_response.get("success"):
                        rpc.response_len_setter(response_len=1)
                        referral_response = rpc.publish(
                            message={
                                "dealership": {
                                    "action": "get_referral_number",
                                    "body": {}
                                }
                            },
                            headers={'dealership': True}
                        ).get("dealership", {})
                        if referral_response.get("success"):
                            rpc.response_len_setter(response_len=1)
                            product_response = rpc.publish(
                                message={
                                    "product": {
                                        "action": "add_to_reserve_dealership",
                                        "body": {
                                            "referral_number": referral_response.get("message"),
                                            "customer_id": user.get("user_id"),
                                            "customer_type": user.get("customer_type")[0],

                                            "data": data.dict(),
                                        }
                                    }
                                },
                                headers={'product': True}
                            ).get("product", {})
                            if product_response.get("success"):
                                # rpc.response_len_setter(response_len=1)
                                # reduce_credit = rpc.publish(
                                #     message={
                                #         "credit": {
                                #             "action": "consume_remaining_credit",
                                #             "body": {
                                #                 "referral_number": referral_response.get("message"),
                                #                 "amount": compare_digits_response.get("total_price"),
                                #                 "customer_id": user.get("user_id"),
                                #                 "total_items": compare_digits_response.get("total_item")
                                #             }
                                #         }
                                #     },
                                #     headers={'credit': True}
                                # ).get("credit", {})
                                # if reduce_credit.get("success"):
                                rpc.response_len_setter(response_len=1)
                                insert_response = rpc.publish(
                                    message={
                                        "dealership": {
                                            "action": "insert_goods_request",
                                            "body": {
                                                "referral_number": referral_response.get("message"),
                                                "customer_id": str(user.get("user_id")),
                                                "customer_name": customer_first_name + " " + customer_last_name,
                                                "total_price": compare_digits_response.get("total_price"),
                                                "data": data.dict()
                                            }
                                        }
                                    },
                                    headers={'dealership': True}
                                ).get("dealership", {})
                                if insert_response.get("success"):
                                    return insert_response
                                return insert_response
                                # return reduce_credit
                            return product_response
                        return referral_response
                    return compare_digits_response
                return check_credit
            return dealership_response
        return customer_response

