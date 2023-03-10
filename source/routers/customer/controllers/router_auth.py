from fastapi import Response, Depends, HTTPException, status, APIRouter

from source.message_broker.rabbit_server import RabbitRPC
from source.routers.customer.module.auth import AuthHandler
from source.routers.customer.validators import validation_auth

router_auth = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

auth_handler = AuthHandler()


@router_auth.get("/")
def mobile_number_validation_generator():
    """
    generate and send mobile number validations to front side
    :return: front-end required values for generate form
    """
    return validation_auth.CustomerAuth.schema().get("properties").copy()


@router_auth.post("/")
def check_is_registered(
        response: Response,
        value: validation_auth.CustomerAuth
):
    """
    for generate mobile number and validate it
    :param response: as annotation
    :param value: as annotation
    :return: Response
    """
    # customer_result = new_rpc.publish(
    #     message=[ra.check_is_registered(customer_phone_number=value.customer_phone_number)]
    # )
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        customer_result = rpc.publish(
            message={
                "customer": {
                    "action": "check_is_registered",
                    "body": {
                        "customer_phone_number": value.customer_phone_number
                    }
                }
            },
            headers={'customer': True}
        ).get("customer", {})
    if not customer_result.get("success"):
        raise HTTPException(
            status_code=customer_result.get("status_code", 500),
            detail={"error": customer_result.get("error", "Something went wrong")}
        )
    response.status_code = customer_result.get("status_code", 200)
    return customer_result.get("message")


@router_auth.post("/send-otp/")
def send_otp_code(value: validation_auth.CustomerAuth, response: Response):
    # customer_result = new_rpc.publish(
    #     message=[ra.send_otp_code(customer_phone_number=value.customer_phone_number)]
    # )
    customer_type = [value.customer_type] if value.customer_type else ["B2B"]
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        customer_result = rpc.publish(
            message={
                "customer": {
                    "action": "send_otp_code",
                    "body": {
                        "customer_phone_number": value.customer_phone_number,
                        "customer_type": customer_type
                    }
                }
            },
            headers={'customer': True}
        ).get("customer", {})
    if not customer_result.get("success"):
        raise HTTPException(
            status_code=customer_result.get("status_code", 500),
            detail={"error": customer_result.get("error", "Something went wrong")}
        )
    response.status_code = customer_result.get("status_code", 200)
    return customer_result.get("message")


@router_auth.post("/verify-otp/")
def verify_otp_code(value: validation_auth.CustomerVerifyOTP, response: Response):
    # customer_result = new_rpc.publish(
    #     message=[
    #         ra.verify_otp_code(customer_phone_number=value.customer_phone_number, customer_code=value.customer_code)]
    # )
    customer_type = [value.customer_type] if value.customer_type else ["B2B"]
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        customer_result = rpc.publish(
            message={
                "customer": {
                    "action": "verify_otp_code",
                    "body": {
                        "customer_phone_number": value.customer_phone_number,
                        "customer_code": value.customer_code,
                        "customer_type": customer_type
                    }
                }
            },
            headers={'customer': True}
        ).get("customer", {})
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
    # try:
    #     del customer_result.get("message")["data"]
    # except KeyError:
    #     ...
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
    # customer_result = new_rpc.publish(
    #     message=[
    #         ra.checking_login_otp_code(customer_phone_number=value.customer_phone_number,
    #                                    customer_code=value.customer_code)]
    # )
    customer_type = [value.customer_type] if value.customer_type else ["B2B"]
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        customer_result = rpc.publish(
            message={
                "customer": {
                    "action": "checking_login_otp_code",
                    "body": {
                        "customer_phone_number": value.customer_phone_number,
                        "customer_code": value.customer_code,
                        "customer_type": customer_type
                    }
                }
            },
            headers={'customer': True}
        ).get("customer", {})
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
    customer_type = [value.customer_type] if value.customer_type else ["B2B"]
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        customer_result = rpc.publish(
            message={
                "customer": {
                    "action": "checking_login_password",
                    "body": {
                        "customer_phone_number": value.customer_phone_number,
                        "customer_password": value.customer_password,
                        "customer_type": customer_type
                    }
                }
            },
            headers={'customer': True}
        ).get("customer", {})
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
    user_name, token_dict = auth_header
    # customer_result = new_rpc.publish(
    #     message=[
    #         ra.save_logout(username=username)]
    # )
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        customer_result = rpc.publish(
            message={
                "customer": {
                    "action": "save_logout",
                    "body": {
                        "username": user_name,
                    }
                }
            },
            headers={'customer': True}
        ).get("customer", {})
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
    # customer_result = new_rpc.publish(
    #     message=[
    #         ra.forget_password(customer_phone_number=user_info.get("phone_number"),
    #                            password=data.customer_password)]
    # )
    print(user_info.get("phone_number"))
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        customer_result = rpc.publish(
            message={
                "customer": {
                    "action": "forget_password",
                    "body": {
                        "customer_phone_number": user_info.get("phone_number"),
                        "password": data.customer_password,
                    }
                }
            },
            headers={'customer': True}
        ).get("customer", {})
    if not customer_result.get("success"):
        raise HTTPException(
            status_code=customer_result.get("status_code", 500),
            detail={"error": customer_result.get("error", "Something went wrong")}
        )
    return customer_result.get("message")
