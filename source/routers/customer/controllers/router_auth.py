import json

from fastapi import Response, Depends, HTTPException, Header
from fastapi import status, APIRouter

from source.message_broker.rabbit_server import RabbitRPC
from source.routers.customer.models.auth import AuthHandler
# from customer.modules.otp import OTP
from source.routers.customer.validators import validation_auth

# from customer.modules import log


router_auth = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

auth_handler = AuthHandler()

rpc = RabbitRPC(exchange_name='headers_exchange', timeout=5)
rpc.connect()
rpc.consume()


# generate and send mobile number validations to front side

@router_auth.get("/")
def mobile_number_validation_generator():
    form = validation_auth.CustomerAuth.schema().get("properties").copy()
    return form


# mobile number generator and validation
@router_auth.post("/")
def check_is_registered(
        response: Response,
        value: validation_auth.CustomerAuth
):
    # TODO fixed status code
    # checking is exist mobile number in db
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
    else:
        response.status_code = customer_result.get("status_code", 200)
        print(customer_result)
        return customer_result.get("message")


@router_auth.post("/send-otp/")
def send_otp_code(value: validation_auth.CustomerAuth, response: Response):
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
    else:
        response.status_code = customer_result.get("status_code", 200)
        return customer_result.get("message")


@router_auth.post("/verify-otp/")
def verify_otp_cod(value: validation_auth.CustomerVerifyOTP, response: Response):
    # TODO fixed status code
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
    else:
        response.status_code = customer_result.get("status_code", 200)
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
    else:
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
    form = validation_auth.CustomerVerifyPassword.schema().get("properties").copy()
    return {"fields": json.dumps(form)}


@router_auth.post("/login/password/")
def checking_login_password(
        value: validation_auth.CustomerVerifyPassword,
        response: Response,
):
    # TODO fixed status code
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
    else:
        customer_info = customer_result.get("message").get('data')
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
    else:
        response.status_code = customer_result.get("status_code", 202)
        return customer_result.get("message")
