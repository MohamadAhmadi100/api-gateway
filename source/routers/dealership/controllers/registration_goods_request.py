from fastapi import Depends, APIRouter
from source.message_broker.rabbit_server import RabbitRPC
from source.routers.customer.module.auth import AuthHandler
from source.routers.dealership.validators.register_request import RequestGoods


router = APIRouter()
auth_handler = AuthHandler()


@router.post("/create_request_goods", tags=["request for goods from dealership"])
def create_request(data: RequestGoods,
                   auth_header=Depends(auth_handler.check_current_user_tokens)):
    user, token = auth_header
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        check_credit = rpc.publish(
            message={
                "credit": {
                    "action": "check_credit",
                    "body": {
                        "customer_id": user.get("user_id")
                    }
                }
            },
            headers={'credit': True}
        ).get("credit", {})
        if check_credit.get("success"):
            rpc.response_len_setter(response_len=1)
            dict_data = data.dict()
            compare_digits_response = rpc.publish(
                message={
                    "dealership": {
                        "action": "check_credit_state",
                        "body": {
                            "credit": check_credit.get("remaining_amount"),
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
                    quantity_response = rpc.publish(
                        message={
                            "quantity": {
                                "action": "add_to_reserve_dealership",
                                "body": {
                                    "referral_number": referral_response.get("message"),
                                    "customer_id": str(user.get("user_id")),
                                    "customer_type": user.get("customer_type"),
                                    "data": data.dict(),
                                }
                            }
                        },
                        headers={'quantity': True}
                    ).get("quantity", {})
                    if quantity_response.get("success"):
                        rpc.response_len_setter(response_len=1)
                        reduce_credit = rpc.publish(
                            message={
                                "credit": {
                                    "action": "consume_remaining_credit",
                                    "body": {
                                        "referral_number": referral_response.get("message"),
                                        "amount": compare_digits_response.get("total_price"),
                                        "customer_id": user.get("user_id")
                                        #TODO send total item
                                    }
                                }
                            },
                            headers={'credit': True}
                        ).get("credit", {})
                        if reduce_credit.get("success"):
                            rpc.response_len_setter(response_len=1)
                            insert_response = rpc.publish(
                                message={
                                    "dealership": {
                                        "action": "insert_goods_request",
                                        "body": {
                                            "referral_number": referral_response.get("message"),
                                            "customer_id": str(user.get("user_id")),
                                            "data": data.dict()
                                        }
                                    }
                                },
                                headers={'dealership': True}
                            ).get("dealership", {})
                            if insert_response.get("success"):
                                return insert_response
                            return insert_response
                        return reduce_credit
                    return quantity_response
                return referral_response
            return compare_digits_response
        return check_credit