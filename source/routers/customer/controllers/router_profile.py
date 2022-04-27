import json
from fastapi import APIRouter, Depends, HTTPException
from fastapi import Response, status
from pydantic.error_wrappers import ValidationError
from source.message_broker.rabbit_server import RabbitRPC
from source.routers.customer.module.auth import AuthHandler
from source.helpers.create_class import CreateClass
from source.routers.customer.validators import validation_profile
from source.routers.customer.validators.validation_profile import EditProfile, get_profile_attributes

# from source.routers.customer.validators import validation_profile, validation_auth

router_profile = APIRouter(
    prefix="/profile",
    tags=["profile"]
)

auth_handler = AuthHandler()

rpc = RabbitRPC(exchange_name='headers_exchange', timeout=5)
rpc.connect()
rpc.consume()


@router_profile.get("/")
def get_profile(
        response: Response,
        auth_header=Depends(auth_handler.check_current_user_tokens),
):
    user_data, header = auth_header
    rpc.response_len_setter(response_len=1)
    result = rpc.publish(
        message={
            "customer": {
                "action": "get_profile",
                "body": {
                    "customer_phone_number": user_data,
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
    rpc.response_len_setter(response_len=1)
    result = rpc.publish(
        message={
            "attribute": {
                "action": "get_all_attributes_by_assignee",
                "body": {
                    "name": "customer"
                }
            }
        },
        headers={'attribute': True}
    )
    attribute_result = result.get("attribute", {})
    if not attribute_result.get("success"):
        raise HTTPException(status_code=attribute_result.get("status_code", 500),
                            detail={"error": attribute_result.get("error", "Something went wrong")})
    customer_data = customer_result.get("message", {})
    attributes = attribute_result.get("message", [])
    valid_attrs = []
    for attr in attributes:
        if customer_data.get(attr.get("name")) is None or not None:
            attr["value"] = customer_data.get(attr.get("name"))
            valid_attrs.append(attr)
    response.status_code = status.HTTP_200_OK
    response.headers["accessToken"] = header.get("access_token")
    response.headers["refresh_token"] = header.get("refresh_token")
    return valid_attrs


@router_profile.put("/")
def edit_profile_data(
        response: Response,
        value: EditProfile,
        auth_header=Depends(auth_handler.check_current_user_tokens),
):
    user_data, header = auth_header
    rpc.response_len_setter(response_len=1)
    result = rpc.publish(
        message={
            "attribute": {
                "action": "get_all_attributes_by_assignee",
                "body": {
                    "name": "customer"
                }
            }
        },
        headers={'attribute': True}
    )
    attribute_result = result.get("attribute", {})
    if not attribute_result.get("success"):
        return HTTPException(status_code=attribute_result.get("status_code", 500),
                             detail={"error": attribute_result.get("error", "Something went wrong")})
    attrs = {obj.get("name"): obj for obj in attribute_result.get("message")}
    profile_model = CreateClass(class_name="EditProfileModel", attributes=attrs).get_pydantic_class()
    try:
        profile_object = profile_model(**value.data)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail={"error": e.errors()}) from e
    rpc.response_len_setter(response_len=1)
    result = rpc.publish(
        message={
            "customer": {
                "action": "edit_profile_data",
                "body": {
                    "customer_phone_number": user_data.get("phone_number"),
                    "data": profile_object.json()
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
    sub_dict = {
        "user_id": user_data.get('user_id'),
        "customer_type": user_data.get('customer_type'),
        "phone_number": user_data.get('phone_number'),
    }
    response.headers["refreshToken"] = auth_handler.encode_refresh_token(sub_dict)
    response.headers["accessToken"] = auth_handler.encode_access_token(sub_dict)
    response.status_code = customer_result.get("status_code", 202)
    return customer_result.get("message", 202)


@router_profile.put("/change-password")
def change_customer_password(
        response: Response,
        data: validation_profile.ChangePassword,
        auth_header=Depends(auth_handler.check_current_user_tokens),
):
    response.status_code = status.HTTP_202_ACCEPTED
    user_data, token_dict = auth_header
    rpc.response_len_setter(response_len=1)
    result = rpc.publish(
        message={
            "customer": {
                "action": "change_customer_password",
                "body": {
                    "data": {
                        "customer_phone_number": user_data.get("phone_number"),
                        "customer_old_password": data.oldPassword,
                        "customer_new_password": data.newPassword
                    }
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
    sub_dict = {
        "user_id": user_data.get('user_id'),
        "customer_type": user_data.get('customer_type'),
        "phone_number": user_data.get('phone_number'),
    }
    response.headers["refreshToken"] = auth_handler.encode_refresh_token(sub_dict)
    response.headers["accessToken"] = auth_handler.encode_access_token(sub_dict)
    response.status_code = customer_result.get("status_code", 202)
    return customer_result.get("message", 202)
