import re

import codemelli
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi import Response, status
from pydantic.error_wrappers import ValidationError

from source.helpers import case_converter
from source.helpers.create_class import CreateClass
from source.helpers.rabbit_config import new_rpc
from source.routers.customer.module.auth import AuthHandler
from source.routers.customer.validators.validation_profile import EditProfile, Delivery, Person, ChangePassword
import source.services.customer.router_profile as profile_funcs
import source.services.attribute.assignee_controller as attribute_funcs
import source.services.kosar.router_customer as customer_funcs
import source.services.customer.router_back_office as back_office_funcs

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
    customer_result = new_rpc.publish(
        message=[profile_funcs.get_profile(customer_phone_number=user_data)]
    )
    if not customer_result.get("success"):
        raise HTTPException(
            status_code=customer_result.get("status_code", 500),
            detail={"error": customer_result.get("error", "Something went wrong")}
        )
    attribute_result = new_rpc.publish(
        message=[attribute_funcs.get_all_attributes_by_assignee(name="customer")]
    )
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
                valid_attrs.append({"profileStatus": "اعتبار سنجی شماره موبایل"})
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
    customer_result = new_rpc.publish(
        message=[profile_funcs.edit_profile_data(customer_phone_number=user_data.get("phone_number"), data=value.json())]
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
    response.status_code = customer_result.get("status_code", 317)
    return customer_result.get("message")


@router_profile.put("/change-password")
def change_customer_password(
        response: Response,
        data: ChangePassword,
        auth_header=Depends(auth_handler.check_current_user_tokens),
):
    user_data, token_dict = auth_header
    data = {
        "customer_phone_number": user_data.get("phone_number"),
        "customer_old_password": data.oldPassword,
        "customer_new_password": data.newPassword
    }
    customer_result = new_rpc.publish(
        message=[profile_funcs.change_customer_password(data=data)]
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
    response.status_code = customer_result.get("status_code", 202)
    return customer_result.get("message", 202)


@router_profile.get("/delivery")
def get_delivery_persons(response: Response,
                         auth_header=Depends(auth_handler.check_current_user_tokens)
                         ):
    user_data, header = auth_header
    customer_result = new_rpc.publish(
        message=[profile_funcs.get_delivery_persons(data={
            "customer_phone_number": user_data.get("phone_number"),
        })]
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


@router_profile.post("/delivery")
def add_delivery_person(response: Response,
                        delivery: Delivery = None,
                        auth_header=Depends(auth_handler.check_current_user_tokens)
                        ):
    if delivery is None:
        delivery = Delivery()
    user_data, header = auth_header
    data = {
        "customer_phone_number": user_data.get("phone_number"),
        "delivery": delivery.json(),
    }
    customer_result = new_rpc.publish(
        message=[profile_funcs.add_delivery_person(data=data)]
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


# ================================================= informal ===========================================================


@router_profile.post("/informal")
def create_informal(person: Person, response: Response, auth_header=Depends(auth_handler.check_current_user_tokens)):
    user_data, header = auth_header
    attribute_result = new_rpc.publish(
        message=[attribute_funcs.get_all_attributes_by_assignee(name="informal")]
    )
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

        try:
            if not codemelli.validator(person_object.informalNationalID):
                raise HTTPException(status_code=422, detail={"error": "کد ملی وارد شده صحیح نمی باشد"})
        except Exception as e:
            raise HTTPException(status_code=422, detail={"error": "کد ملی وارد شده صحیح نمی باشد"}) from e
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
    customer_result = new_rpc.publish(
        message=[profile_funcs.create_informal(data={
            "customer_mobile_number": user_data.get("phone_number"),
            "informal": person_object.json()
        })]
    )
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

    kosar_result = new_rpc.publish(
        message=[customer_funcs.get_customer_kosar_data(data=kosar_data)]
    )
    kosar_data = kosar_result.get("message")
    new_rpc.publish(
        message=[back_office_funcs.set_kosar_data(mobileNumber=user_data.get("phone_number"), kosarData=kosar_data)]
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
    data = {
        "customer_mobile_number": user_data.get("phone_number"),
        "informal_national_id": informalNationalId
    }
    customer_result = new_rpc.publish(
        message=[profile_funcs.get_informal(data=data)]
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


@router_profile.get("/informal_persons")
def get_informal_persons(
        response: Response,
        auth_header=Depends(auth_handler.check_current_user_tokens)
):
    user_data, header = auth_header
    customer_result = new_rpc.publish(
        message=[profile_funcs.get_all_informal_persons(data={
            "customer_mobile_number": user_data.get("phone_number"),
        })]
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
