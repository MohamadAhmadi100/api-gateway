from fastapi import APIRouter
from fastapi import Response, Depends

from source.message_broker.rabbit_server import RabbitRPC
from source.routers.credit.validators.dealership_validator import AddCredit, AcceptCredit
from source.routers.customer.helpers.profile_view import get_profile_info
from source.routers.customer.module.auth import AuthHandler

credit = APIRouter()
auth_handler = AuthHandler()


@credit.post("/create_credit", tags=["customer_side"])
def customer_credit(response: Response,
                    auth_header=Depends(auth_handler.check_current_user_tokens)):
    user, auth = auth_header
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        order_response = rpc.publish(
            message={
                "credit": {
                    "action": "create_customer_dealership_credit",
                    "body": {
                        "customer_id": user.get("user_id"),
                    }
                }
            },
            headers={'credit': True}
        ).get("credit", {})
        response.status_code = 200
        return order_response


@credit.post("/add_credit", tags=["customer_side"])
def request_dealership_credit(response: Response, data: AddCredit,
                              auth_header=Depends(auth_handler.check_current_user_tokens)):
    user, auth = auth_header
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        customer = get_profile_info(auth_header[0])
        order_response = rpc.publish(
            message={
                "credit": {
                    "action": "request_dealership_credit",
                    "body": {
                        "customer_id": user.get("user_id"),
                        "customer_name": f"{customer['customerFirstName']} {customer['customerLastName']}",
                        "customer_telephone": customer['customerPhoneNumber'],
                        "amount": data.amount,
                        "payment_type": data.payment_type,
                    }
                }
            },
            headers={'credit': True}
        ).get("credit", {})
        response.status_code = 200
        return order_response


@credit.post("/accept_credit", tags=["customer_side"])
def accept_dealership_credit(response: Response, data: AcceptCredit,
                             ):
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        order_response = rpc.publish(
            message={
                "credit": {
                    "action": "accept_request_dealership_credit",
                    "body": {
                        "referral_number": data.referral_number,
                    }
                }
            },
            headers={'credit': True}
        ).get("credit", {})
        response.status_code = 200
        return order_response


@credit.post("/get_remaining_credit", tags=["customer_side"])
def get_remaining_credit(response: Response,
                         auth_header=Depends(auth_handler.check_current_user_tokens)):
    user, auth = auth_header
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
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
        response.status_code = 200
        if dealership_response.get("success"):
            rpc.response_len_setter(response_len=1)
            credit_response = rpc.publish(
                message={
                    "credit": {
                        "action": "get_credit",
                        "body": {
                            "customer_id": user.get("user_id"),
                            "products_value": dealership_response.get("message")
                        }
                    }
                },
                headers={'credit': True}
            ).get("credit", {})
            if credit_response.get("success"):
                return credit_response
            return credit_response
        return dealership_response
