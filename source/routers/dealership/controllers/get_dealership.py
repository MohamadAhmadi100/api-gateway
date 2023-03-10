from fastapi import APIRouter, Depends, Query
from typing import Optional
from source.message_broker.rabbit_server import RabbitRPC
from source.routers.customer.module.auth import AuthHandler
from source.routers.dealership.validators.get_request_goods_form import GetRequestGood
from source.routers.dealership.validators.get_sell_forms import SellForms
from source.routers.dealership.validators.register_request import SubmitRequestForms

router = APIRouter()
auth_handler = AuthHandler()


@router.get("/get_dealership_inventory", tags=["dealerships panel details (ecommerce)"])
def products_list(
        imei: Optional[str] = Query(default=None),
        product_name: Optional[str] = Query(default=None),
        auth_header=Depends(auth_handler.check_current_user_tokens),
):
    user, token = auth_header
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        get_list_response = rpc.publish(
            message={
                "dealership": {
                    "action": "get_dealership_inventory",
                    "body": {
                        "customer_id": str(user.get("user_id")),
                        "imei": imei,
                        "product_name": product_name

                    }
                }
            },
            headers={'dealership': True}
        ).get("dealership", {})
        if get_list_response.get("success"):
            return get_list_response
        return get_list_response


@router.get("/get_initial", tags=["dealerships panel details (ecommerce)"])
def initial(
        auth_header=Depends(auth_handler.check_current_user_tokens)
):
    user, token = auth_header
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        get_initial = rpc.publish(
            message={
                "dealership": {
                    "action": "get_initial",
                    "body": {
                        "customer_id": str(user.get("user_id"))
                    }
                }
            },
            headers={'dealership': True}
        ).get("dealership", {})
        if get_initial.get("success"):
            return get_initial
        return get_initial


@router.post("/get_sell_forms", tags=["dealerships panel details (ecommerce)"])
def get_sell_forms(
        parameters: SellForms,
        auth_header=Depends(auth_handler.check_current_user_tokens)
):
    parameters = parameters.dict()
    user, token = auth_header
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        response = rpc.publish(
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
        if response.get("success"):
            return response
        return response


@router.post("/get_request_goods_forms", tags=["dealerships panel details (ecommerce)"])
def get_request_goods_forms(
        parameters: GetRequestGood,
        auth_header=Depends(auth_handler.check_current_user_tokens)
):
    user, token = auth_header
    parameters = parameters.dict()
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        get_forms_response = rpc.publish(
            message={
                "dealership": {
                    "action": "get_request_goods_forms",
                    "body": {
                        "customer_id": str(user.get("user_id")),
                        "page": parameters.get("page"),
                        "per_page": parameters.get("per_page"),
                        "referral_number": parameters.get("referral_number"),
                        "date_from": parameters.get("date_from"),
                        "date_to": parameters.get("date_to"),
                        "status": parameters.get("status")
                    }
                }
            },
            headers={'dealership': True}
        ).get("dealership", {})
        if get_forms_response.get("success"):
            return get_forms_response
        return get_forms_response


############################# Back office ###########################################


@router.post("/get_request_forms", tags=["back office"])
def get_request_goods_forms(
        parameters: GetRequestGood,
        # auth_header=Depends(auth_handler.check_current_user_tokens)
):
    # user, token = auth_header
    parameters = parameters.dict()
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        get_forms_response = rpc.publish(
            message={
                "dealership": {
                    "action": "get_request_forms",
                    "body": {
                        "page": parameters.get("page"),
                        "per_page": parameters.get("per_page"),
                        "referral_number": parameters.get("referral_number"),
                        "customer_name": parameters.get("customer_name"),
                        "date_from": parameters.get("date_from"),
                        "date_to": parameters.get("date_to"),
                        "status": parameters.get("status")
                    }
                }
            },
            headers={'dealership': True}
        ).get("dealership", {})
        if get_forms_response.get("success"):
            return get_forms_response
        return get_forms_response


@router.post("/get_request_forms_pending", tags=["back office"])
def get_request_goods_forms(
        parameters: GetRequestGood,
        # auth_header=Depends(auth_handler.check_current_user_tokens)
):
    # user, token = auth_header
    parameters = parameters.dict()
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        get_forms_response = rpc.publish(
            message={
                "dealership": {
                    "action": "get_request_forms",
                    "body": {
                        "page": parameters.get("page"),
                        "per_page": parameters.get("per_page"),
                        "referral_number": parameters.get("referral_number"),
                        "customer_name": parameters.get("customer_name"),
                        "date_from": parameters.get("date_from"),
                        "date_to": parameters.get("date_to"),
                        "status": "pending"
                    }
                }
            },
            headers={'dealership': True}
        ).get("dealership", {})
        if get_forms_response.get("success"):
            return get_forms_response
        return get_forms_response


@router.put("/submit_request_forms", tags=["back office"])
def submit_request_forms(
        parameters: SubmitRequestForms,
        # auth_header=Depends(auth_handler.check_current_user_tokens)
):
    # user, token = auth_header
    parameters = parameters.dict()
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        product_response = rpc.publish(
            message={
                "product": {
                    "action": "add_to_reserve_dealership",
                    "body": {
                        "referral_number": parameters.get("referral_number"),
                        "customer_id": parameters.get("customer_id"),
                        "customer_type": "B2B",
                        "data": parameters.get("details"),
                    }
                }
            },
            headers={'product': True}
        ).get("product", {})
        if product_response.get("success"):
            submit_status_response = rpc.publish(
                message={
                    "dealership": {
                        "action": "change_request_form_status",
                        "body": {
                            "referral_number": parameters.get("referral_number"),
                        }
                    }
                },
                headers={'dealership': True}
            ).get("dealership", {})
            if submit_status_response.get("success"):
                return submit_status_response
            return submit_status_response
        return product_response