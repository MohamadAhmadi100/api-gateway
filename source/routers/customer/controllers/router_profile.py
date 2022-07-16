import re

import codemelli
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi import Response, status
from pydantic.error_wrappers import ValidationError

from source.helpers import case_converter
from source.helpers.create_class import CreateClass
from source.message_broker.rabbit_server import RabbitRPC
# from source.message_broker.rabbitmq import RabbitRPC as RabbitRPC_Test
from source.routers.customer.module.auth import AuthHandler
from source.routers.customer.validators import validation_profile
from source.routers.customer.validators.validation_profile import EditProfile, Delivery, Person

router_profile = APIRouter(
    prefix="/profile",
    tags=["profile"]
)

auth_handler = AuthHandler()

# test_rpc = RabbitRPC_Test(exchange_name='headers_exchange', timeout=20)


@router_profile.get("/")
def get_profile(
        response: Response,
        auth_header=Depends(auth_handler.check_current_user_tokens),
):
    user_data, header = auth_header
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        result = rpc.publish(
            # result = test_rpc.publish(
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
        # result = test_rpc.publish(
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
    confirm = False
    mobile_confirm = False
    for attr in valid_attrs:
        if attr.get("name") == "customerStatus":
            if attr.get("value") == "cancel":
                valid_attrs.append({"profileStatus": "لغو شده"})
            if attr.get("value") == "pend":
                valid_attrs.append({"profileStatus": "در انتظار تایید"})
            if attr.get("value") == "confirm":
                confirm = True
        if attr.get("name") == "customerIsMobileConfirm":
            if not attr.get("value"):
                valid_attrs.append({"profileStatus": "در انتظار تایید شماره موبایل"})
            elif attr.get("value"):
                mobile_confirm = True
    if mobile_confirm and confirm:
        valid_attrs.append({"profileStatus": "تایید شده"})
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
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
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


# ================================================= informal ===========================================================


@router_profile.post("/informal")
def create_informal(person: Person, response: Response, auth_header=Depends(auth_handler.check_current_user_tokens)):
    user_data, header = auth_header
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        result = rpc.publish(
            message={
                "attribute": {
                    "action": "get_all_attributes_by_assignee",
                    "body": {
                        "name": "informal"
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
    person_model = CreateClass(class_name="InformalPersonModel", attributes=attrs).get_pydantic_class()
    try:
        person_object = person_model(**person.data)
        pattern = "^[0-9]{10}$"
        national_id_match = re.fullmatch(pattern, person_object.informalNationalID)

        if not national_id_match:
            raise HTTPException(status_code=422, detail={"error": "کد ملی وارد شده نادرست است"})
        # if not codemelli.validator(person_object.informalNationalID):
        #     raise HTTPException(status_code=422, detail={"error": "کد ملی وارد شده صحیح نمی باشد"})
        pattern = r"^09[0-9]{9}$"
        mobile_number_match = re.fullmatch(pattern, person_object.informalMobileNumber)
        if not mobile_number_match:
            raise HTTPException(status_code=422, detail={"error": "شماره تلفن وارد شده صحیح نمیباشد"})
        first_name_match = re.fullmatch("^[\\u0600-\\u06FF ]{2,32}$", person_object.informalFirstName)
        if not first_name_match:
            raise HTTPException(status_code=422, detail={"error": "نام وارد شده صحیح نمیباشد"})
        last_name_match = re.fullmatch("^[\\u0600-\\u06FF ]{2,32}$", person_object.informalLastName)
        if not last_name_match:
            raise HTTPException(status_code=422, detail={"error": "نام خانوادگی وارد شده صحیح نمیباشد"})
    except ValidationError as e:
        raise HTTPException(status_code=422, detail={"error": e.errors()}) from e
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        result = rpc.publish(
            message={
                "customer": {
                    "action": "create_informal",
                    "body": {
                        "data": {
                            "customer_mobile_number": user_data.get("phone_number"),
                            "informal": person_object.json()
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
    kosar_data = customer_result.get("kosarData")
    if not kosar_data:
        sub_dict = {
            "user_id": user_data.get('user_id'),
            "customer_type": user_data.get('customer_type'),
            "phone_number": user_data.get('phone_number'),
        }
        response.headers["refreshToken"] = auth_handler.encode_refresh_token(sub_dict)
        response.headers["accessToken"] = auth_handler.encode_access_token(sub_dict)
        response.status_code = customer_result.get("status_code", 200)
        return {"message": "کاربر غیر رسمی با موفقیت ثبت شد"}
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        result = rpc.publish(
            message={
                "kosar": {
                    "action": "get_customer_kosar_data",
                    "body": {
                        "data": kosar_data
                    }
                }
            },
            headers={'kosar': True}
        )
    kosar_result = result.get("kosar", {})
    kosar_data = kosar_result.get("message")
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        rpc.publish(
            message={
                "customer": {
                    "action": "set_kosar_data",
                    "body": {
                        "mobileNumber": user_data.get("phone_number"),
                        "kosarData": kosar_data
                    }
                }
            },
            headers={'customer': True}
        )
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


@router_profile.get("/informal")
def get_informal(
        response: Response,
        informalNationalId: str = Query(..., alias="informalNationalId"),
        auth_header=Depends(auth_handler.check_current_user_tokens)
):
    user_data, header = auth_header
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        result = rpc.publish(
            message={
                "customer": {
                    "action": "get_informal",
                    "body": {
                        "data": {
                            "customer_mobile_number": user_data.get("phone_number"),
                            "informal_national_id": informalNationalId
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


@router_profile.get("/informal_persons")
def get_informal_persons(
        response: Response,
        auth_header=Depends(auth_handler.check_current_user_tokens)
):
    user_data, header = auth_header
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        result = rpc.publish(
            message={
                "customer": {
                    "action": "get_all_informal_persons",
                    "body": {
                        "data": {
                            "customer_mobile_number": user_data.get("phone_number"),
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
