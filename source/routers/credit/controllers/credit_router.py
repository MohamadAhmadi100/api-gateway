from fastapi import APIRouter, Response, Depends, Query
from source.message_broker.rabbit_server import RabbitRPC
from source.routers.credit.validators.credit_validator import AddCredit, AcceptCredit, RequestsDetail, \
    AccountingRecords, ChangePaymentStatus
from source.routers.customer.helpers.profile_view import get_profile_info
from source.routers.customer.module.auth import AuthHandler
from source.routers.dealership.validators.get_sell_forms import SellForms

credit = APIRouter()
auth_handler = AuthHandler()


############################# Customer Side ###########################################

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


@credit.post("/request_credit", tags=["customer_side"])
def request_dealership_credit(response: Response, data: AddCredit,
                              auth_header=Depends(auth_handler.check_current_user_tokens)):
    user, auth = auth_header
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        customer = get_profile_info(auth_header[0])
        credit_response = rpc.publish(
            message={
                "credit": {
                    "action": "request_dealership_credit",
                    "body": {
                        "customer_id": user.get("user_id"),
                        "customer_name": f"{customer['customerFirstName']} {customer['customerLastName']}",
                        "customer_telephone": customer['customerPhoneNumber'],
                        "amount": data.amount,
                        "payment_type": data.payment_type,
                        "description": data.description,
                        "accepted": data.accepted
                    }
                }
            },
            headers={'credit': True}
        )
        response.status_code = 200
        return credit_response


@credit.get("/get_remaining_credit", tags=["customer_side"])
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
                        "action": "get_remaining_credit",
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


@credit.post("/get_credit_return_list", tags=["customer_side"])
def get_credit_return_list(
        parameters: SellForms,
        auth_header=Depends(auth_handler.check_current_user_tokens)
):

    user, auth = auth_header
    parameters = parameters.dict()
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        order_response = rpc.publish(
            message={
                "order": {
                    "action": "get_orders_list_dealership",
                    "body": {
                        "dealership_id": user.get("user_id"),
                        "customer_id": parameters.get("customer_id"),
                        "page": parameters.get("page"),
                        "per_page": parameters.get("per_page"),
                        "order_number": parameters.get("order_number"),
                        "payment_status": parameters.get("payment_status"),
                        "customer_name": parameters.get("customer_name"),
                        "date_from": parameters.get("date_from"),
                        "date_to": parameters.get("date_to"),
                        "status": parameters.get("status"),
                    }
                }
            },
            headers={'order': True}
        ).get("order", {})
        if order_response.get("success"):
            rpc.response_len_setter(response_len=1)
            dealership_response = rpc.publish(
                message={
                    "dealership": {
                        "action": "calculate_credit_per_product",
                        "body": {
                            "orders": order_response.get("message"),
                        }
                    }
                },
                headers={'dealership': True}
            ).get("dealership", {})
            if dealership_response.get("success"):
                return dealership_response
            return dealership_response
        return order_response


@credit.post("/get_credit_requests", tags=["customer_side"])
def get_credit_requests(response: Response, data: RequestsDetail,
                        auth_header=Depends(auth_handler.check_current_user_tokens)):
    user, auth = auth_header
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        customer = get_profile_info(auth_header[0])
        requests_details = data.dict()
        credit_response = rpc.publish(
            message={
                "credit": {
                    "action": "get_credit_requests",
                    "body": {
                        "customer_id": user.get("user_id"),
                        "referral_number": requests_details.get("referral_number"),
                        "date_from": requests_details.get("date_from"),
                        "date_to": requests_details.get("date_to"),
                        "page": requests_details.get("page"),
                        "per_page": requests_details.get("per_page"),
                        "amount_from": requests_details.get("amountFrom"),
                        "amount_to": requests_details.get("amountTo"),
                        "accepted": requests_details.get("accepted"),
                        "search_box": requests_details.get("search_box"),
                    }
                }
            },
            headers={'credit': True}
        ).get("credit", {})
        if credit_response.get("success"):
            response.status_code = 200
            return credit_response
        return credit_response


############################# Back office ###########################################
@credit.post("/accept_credit", tags=["back office"])
def accept_dealership_credit(response: Response, data: AcceptCredit,
                             ):
    dict_data = data.dict()
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        order_response = rpc.publish(
            message={
                "credit": {
                    "action": "accept_request_dealership_credit",
                    "body": {
                        "referral_number": dict_data.get("referral_number"),
                    }
                }
            },
            headers={'credit': True}
        ).get("credit", {})
        response.status_code = 200
        return order_response


############################# Accounting ###########################################


@credit.post("/get_accounting_records", tags=["Accounting"])
def get_accounting_records(response: Response, data: AccountingRecords,
                           # auth_header=Depends(auth_handler.check_current_user_tokens)
                           ):
    # user, auth = auth_header
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        # customer = get_profile_info(auth_header[0])
        credit_response = rpc.publish(
            message={
                "credit": {
                    "action": "get_accounting_records",
                    "body": {
                        "parameters": data.dict()
                    }
                }
            },
            headers={'credit': True}
        ).get("credit", {})
        if credit_response.get("success"):
            response.status_code = 200
            return credit_response
        return credit_response



@credit.put("/change_payment_status", tags=["Accounting"])
def change_payment_status_per_system_code(response: Response,
                                          incoming_system_codes: ChangePaymentStatus
                                          # auth_header=Depends(auth_handler.check_current_user_tokens)
                                          ):
    # user, auth = auth_header
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        credit_response = rpc.publish(
            message={
                "credit": {
                    "action": "change_payment_status_per_system_code",
                    "body": {
                        "incoming_system_codes": incoming_system_codes.dict()

                    }
                }
            },
            headers={'credit': True}
        )
        if credit_response.get("success"):
            response.status_code = 200
            return credit_response
        return credit_response

