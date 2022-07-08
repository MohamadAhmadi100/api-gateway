import json

from fastapi import Response, Depends, HTTPException
from fastapi import status, APIRouter

from source.message_broker.rabbit_server import RabbitRPC
from source.routers.customer.module.auth import AuthHandler
from source.routers.customer.validators import validation_auth
# from source.message_broker.rabbitmq import RabbitRPC as NewRabbit

# from customer.modules import log


router_auth = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

auth_handler = AuthHandler()

# new_rpc = NewRabbit(exchange_name='headers_exchange', timeout=10)


# generate and send mobile number validations to front side

@router_auth.get("/")
def mobile_number_validation_generator():
    return validation_auth.CustomerAuth.schema().get("properties").copy()


# mobile number generator and validation
@router_auth.post("/")
def check_is_registered(
        response: Response,
        value: validation_auth.CustomerAuth
):
    # checking is exists mobile number in db
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        result = rpc.publish(
            message={
                "customer": {
                    "action": "check_is_registered",
                    "body": {
                        "customer_phone_number": value.customer_phone_number
                    }
                }
            },
            headers={'customer': True}
        )
    customer_result = result.get("customer", {})
    if not customer_result.get("success"):
        raise HTTPException(
            status_code=customer_result.get("status_code", 500),
            detail={"error": customer_result.get("error", "Something went wrong")}
        )
    response.status_code = customer_result.get("status_code", 200)
    return customer_result.get("message")


@router_auth.post("/send-otp/")
def send_otp_code(value: validation_auth.CustomerAuth, response: Response):
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        result = rpc.publish(
            message={
                "customer": {
                    "action": "send_otp_code",
                    "body": {
                        "customer_phone_number": value.customer_phone_number
                    }
                }
            },
            headers={'customer': True}
        )
    customer_result = result.get("customer", {})
    if not customer_result.get("success"):
        raise HTTPException(
            status_code=customer_result.get("status_code", 500),
            detail={"error": customer_result.get("error", "Something went wrong")}
        )
    response.status_code = customer_result.get("status_code", 200)
    return customer_result.get("message")


@router_auth.post("/verify-otp/")
def verify_otp_code(value: validation_auth.CustomerVerifyOTP, response: Response):
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        result = rpc.publish(
            message={
                "customer": {
                    "action": "verify_otp_cod",
                    "body": {
                        "customer_phone_number": value.customer_phone_number,
                        "customer_code": value.customer_code
                    }
                }
            },
            headers={'customer': True}
        )
    customer_result = result.get("customer", {})
    if not customer_result.get("success"):
        raise HTTPException(
            status_code=customer_result.get("status_code", 500),
            detail={"error": customer_result.get("error", "Something went wrong")}
        )
    customer_info = customer_result.get("message").get('data')
    sub_dict = {
        "user_id": customer_info.get('customerID'),
        "customer_type": customer_info.get('customerType'),
        "phone_number": customer_info.get('customerPhoneNumber'),
    }
    response.headers["refreshToken"] = auth_handler.encode_refresh_token(sub_dict)
    response.headers["accessToken"] = auth_handler.encode_access_token(sub_dict)
    response.status_code = customer_result.get("status_code", 200)
    try:
        del customer_result.get("message")["data"]
    except KeyError:
        ...
    return customer_result.get("message")


@router_auth.get("/login/otp/")
def otp_form_generator():
    form = validation_auth.CustomerVerifyOTP.schema().get("properties").copy()
    return {"fields": form}


@router_auth.post("/login/otp/")
def checking_login_otp_code(
        value: validation_auth.CustomerVerifyOTP,
        response: Response,
):
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        result = rpc.publish(
            message={
                "customer": {
                    "action": "checking_login_otp_code",
                    "body": {
                        "customer_phone_number": value.customer_phone_number,
                        "customer_code": value.customer_code
                    }
                }
            },
            headers={'customer': True}
        )
    customer_result = result.get("customer", {})
    if not customer_result.get("success"):
        raise HTTPException(
            status_code=customer_result.get("status_code", 500),
            detail={"error": customer_result.get("error", "Something went wrong")}
        )
    customer_info = customer_result.get("message").get('data')
    sub_dict = {
        "user_id": customer_info.get('customerID'),
        "customer_type": customer_info.get('customerType'),
        "phone_number": customer_info.get('customerPhoneNumber'),
    }
    response.headers["refreshToken"] = auth_handler.encode_refresh_token(sub_dict)
    response.headers["accessToken"] = auth_handler.encode_access_token(sub_dict)

    response.status_code = customer_result.get("status_code", 200)
    return customer_result.get("message")


@router_auth.get("/login/password/")
def otp_form_generator():
    return validation_auth.CustomerVerifyPassword.schema().get("properties").copy()


@router_auth.post("/login/password/")
def checking_login_password(
        value: validation_auth.CustomerVerifyPassword,
        response: Response,
):
    # result = new_rpc.publish(
    #         message={
    #             "customer": {
    #                 "action": "checking_login_password",
    #                 "body": {
    #                     "customer_phone_number": value.customer_phone_number,
    #                     "customer_password": value.customer_password
    #                 }
    #             }
    #         },
    #         headers={'customer': True}
    #     )
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        result = rpc.publish(
            message={
                "customer": {
                    "action": "checking_login_password",
                    "body": {
                        "customer_phone_number": value.customer_phone_number,
                        "customer_password": value.customer_password
                    }
                }
            },
            headers={'customer': True}
        )
    customer_result = result.get("customer", {})
    if not customer_result.get("success"):
        raise HTTPException(
            status_code=customer_result.get("status_code", 500),
            detail={"error": customer_result.get("error", "Something went wrong")}
        )
    customer_info = customer_result.get('data')
    sub_dict = {
        "user_id": customer_info.get('customerID'),
        "customer_type": customer_info.get('customerType'),
        "phone_number": customer_info.get('customerPhoneNumber'),
    }
    response.headers["refreshToken"] = auth_handler.encode_refresh_token(sub_dict)
    response.headers["accessToken"] = auth_handler.encode_access_token(sub_dict)
    response.status_code = customer_result.get("status_code", 200)
    return customer_result


@router_auth.post("/check-token/")
def check_token(
        response: Response,
        auth_header=Depends(auth_handler.check_current_user_tokens)
):
    response.status_code = status.HTTP_202_ACCEPTED
    username, token_dict = auth_header

    response.headers["accessToken"] = token_dict.get("access_token")
    response.headers["refreshToken"] = token_dict.get("refresh_token")
    return {"customer_data": username}


@router_auth.post("/save-logout/")
def save_logout(
        response: Response,
        auth_header=Depends(auth_handler.check_current_user_tokens)
):
    username, token_dict = auth_header
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        result = rpc.publish(
            message={
                "customer": {
                    "action": "save_logout",
                    "body": {
                        "username": username,
                    }
                }
            },
            headers={'customer': True}
        )
    customer_result = result.get("customer", {})
    if not customer_result.get("success"):
        raise HTTPException(
            status_code=customer_result.get("status_code", 500),
            detail={"error": customer_result.get("error", "Something went wrong")}
        )
    response.status_code = customer_result.get("status_code", 202)
    return customer_result.get("message")


@router_auth.post("/forget-password/")
def forget_password(
        data: validation_auth.CustomerForgetPassword,
        auth_header=Depends(auth_handler.check_current_user_tokens),
):
    user_info, token_dict = auth_header
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        result = rpc.publish(
            message={
                "customer": {
                    "action": "forget_password",
                    "body": {
                        "customer_phone_number": user_info.get("phone_number"),
                        "password": data.customer_password
                    }
                }
            },
            headers={'customer': True}
        )
    customer_result = result.get("customer", {})
    if not customer_result.get("success"):
        raise HTTPException(
            status_code=customer_result.get("status_code", 500),
            detail={"error": customer_result.get("error", "Something went wrong")}
        )
    return customer_result.get("message")
