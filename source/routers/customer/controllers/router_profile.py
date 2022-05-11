import json
from fastapi import APIRouter, Depends, HTTPException
from fastapi import Response, status
from pydantic.error_wrappers import ValidationError
from source.message_broker.rabbit_server import RabbitRPC
from source.routers.customer.module.auth import AuthHandler
from source.helpers.create_class import CreateClass
from source.routers.customer.validators import validation_profile
from source.routers.customer.validators.validation_profile import EditProfile, Delivery
from source.helpers import case_converter

router_profile = APIRouter(
    prefix="/profile",
    tags=["profile"]
)

auth_handler = AuthHandler()


@router_profile.get("/")
def get_profile(
        response: Response,
        auth_header=Depends(auth_handler.check_current_user_tokens),
):
    user_data, header = auth_header
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
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
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
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
    for attr in case_converter.convert_case(attributes, "camel"):
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
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
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
    attrs = case_converter.convert_case(attribute_result.get("message"), "camel")
    attrs = {obj.get("name"): obj for obj in attrs}
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
    user_data, token_dict = auth_header
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
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


@router_profile.get("/delivery")
def get_delivery_persons(response: Response,
                         auth_header=Depends(auth_handler.check_current_user_tokens)
                         ):
    user_data, header = auth_header
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        result = rpc.publish(
            message={
                "customer": {
                    "action": "get_delivery_persons",
                    "body": {
                        "data": {
                            "customer_phone_number": user_data.get("phone_number"),
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
    response.status_code = customer_result.get("status_code", 200)
    return customer_result.get("message", 200)


@router_profile.post("/delivery")
def add_delivery_person(response: Response,
                        delivery: Delivery = None,
                        auth_header=Depends(auth_handler.check_current_user_tokens)
                        ):
    if delivery is None:
        delivery = Delivery()
    user_data, header = auth_header
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        result = rpc.publish(
            message={
                "customer": {
                    "action": "add_delivery_person",
                    "body": {
                        "data": {
                            "customer_phone_number": user_data.get("phone_number"),
                            "delivery": delivery.json(),
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
    response.status_code = customer_result.get("status_code", 200)
    return customer_result.get("message", 200)
