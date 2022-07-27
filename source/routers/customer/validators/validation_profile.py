import re
from typing import Optional

import codemelli
from fastapi import HTTPException
from pydantic import BaseModel, validator, Field

from source.helpers.create_class import CreateClass
from source.message_broker.rabbit_server import RabbitRPC


def get_profile_attributes(data):
    rpc = RabbitRPC(exchange_name='headers_exchange', timeout=5)
    rpc.connect()
    rpc.consume()
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
    return CreateClass(class_name="EditProfileModel", attributes=attrs).get_pydantic_class()(**data.attributes)


class EditProfile(BaseModel):
    # data: dict

    customer_first_name: Optional[str] = Field(
        description="",
        title="نام",
        alias="customerFirstName",
        name="customerFirstName",
        placeholder="مهدی",
        minLength=2,
        maxLength=32,
        dataType="string",
        type="text",
        regexPattern=r"^[\u0600-\u06FF]{2,32}$",
        isRquired=False,
    )
    customer_last_name: Optional[str] = Field(
        description="",
        alias="customerLastName",
        title="نام خانوادگی",
        name="customerLastName",
        placeholder="مهدوی",
        minLength=2,
        maxLength=32,
        dataType="string",
        type="text",
        regexPattern=r"^[\u0600-\u06FF]{2,32}$",
        isRquired=False,
    )
    customer_postal_code: Optional[str] = Field(
        alias="customerPostalCode",
        description="",
        title="کد پستی",
        name="customerPostalCode",
        placeholder="4571915113",
        minLength=10,
        maxLength=10,
        dataType="string",
        type="text",
        regexPattern="^[0-9]{10}$",
        isRquired=False,
    )
    customer_email: Optional[str] = Field(
        alias="customerEmail",
        description="",
        title="پست الکترونیک",
        name="customerEmail",
        placeholder="example@me.com",
        minLength=4,
        maxLength=128,
        dataType="string",
        type="text",
        regexPattern=r"^([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+$",
        isRquired=False,
    )
    customer_shop_name: Optional[str] = Field(
        alias="customerShopName",
        description="",
        title="نام شرکت/مغازه",
        name="customerShopName",
        placeholder="",
        minLength=4,
        maxLength=128,
        dataType="string",
        type="text",
        regexPattern=r"^[\u0600-\u06FF]{2,32}$",
        isRquired=False,
    )
    customer_account_number: Optional[str] = Field(
        alias="customerAccountNumber",
        description="",
        title="شماره حساب",
        name="customerAccountNumber",
        placeholder="",
        minLength=4,
        maxLength=128,
        dataType="string",
        type="text",
        regexPattern=r"^[0-9]{7,20}$",
        isRquired=False,
    )
    customer_telephone_number: Optional[str] = Field(
        alias="customerTelephoneNumber",
        description="",
        title="تلفن ثابت",
        name="customerTelephoneNumber",
        placeholder="",
        minLength=4,
        maxLength=128,
        dataType="string",
        type="text",
        regexPattern=r"^0[0-9]{11}$",
        isRquired=False,
    )
    customer_shop_status: Optional[str] = Field(
        alias="customerShopStatus",
        description="",
        title="وضعیت فروشگاه",
        name="customerShopStatus",
        placeholder="",
        minLength=2,
        maxLength=32,
        dataType="string",
        type="text",
        isRquired=False,
    )
    customer_shop_location: Optional[str] = Field(
        alias="customerShopLocation",
        description="",
        title="موقعیت مکانی فروشگاه",
        name="customerShopLocation",
        placeholder="",
        minLength=2,
        maxLength=32,
        dataType="string",
        type="text",
        isRquired=False,
    )
    customer_education: Optional[str] = Field(
        alias="customerEducation",
        description="",
        title="تحصیلات",
        name="customerEducation",
        placeholder="",
        minLength=2,
        maxLength=32,
        dataType="string",
        type="text",
        isRquired=False,
    )
    customer_image: Optional[str] = Field(
        alias="customerImage",
        description="",
        title="عکس پروفایل",
        name="customerImage",
        placeholder="",
        minLength=2,
        maxLength=256,
        dataType="string",
        type="text",
        isRquired=False,
    )
    customer_ofogh_code: Optional[str] = Field(
        alias="customerOfoghCode",
        description="",
        title="کد افق",
        name="customerOfoghCode",
        placeholder="",
        minLength=2,
        maxLength=16,
        dataType="string",
        type="text",
        regexPattern=r"^[0-9]{4,5}$",
        isRquired=False,
    )
    customer_document_status: Optional[str] = Field(
        alias="customerDocumentStatus",
        description="",
        title="وضعیت مدارک",
        name="customerDocumentStatus",
        placeholder="",
        minLength=2,
        maxLength=256,
        dataType="string",
        type="text",
        isRquired=False,
    )
    customer_class: Optional[str] = Field(
        alias="customerClass",
        description="",
        title="صنف",
        name="customerClass",
        placeholder="",
        minLength=2,
        maxLength=32,
        dataType="string",
        type="text",
        regexPattern=r"^[\u0600-\u06FF ]{2,32}$",
        isRquired=False,
    )
    customer_shop_postal_code: Optional[str] = Field(
        alias="customerShopPostalCode",
        description="",
        title="کد پستی محل کسب",
        name="customerShopPostalCode",
        placeholder="",
        minLength=2,
        maxLength=32,
        dataType="string",
        type="text",
        regexPattern=r"^[0-9]*10",
        isRquired=False,
    )

    @validator("customer_first_name")
    def validate_customer_first_name(cls, customer_first_name):
        pattern = r"^[\u0600-\u06FF ]{2,32}$"
        match = re.fullmatch(pattern, customer_first_name)
        if not match:
            raise HTTPException(status_code=422, detail={"error": "نام وارد شده صحیح نمیباشد"})
        return customer_first_name

    @validator("customer_last_name")
    def validate_customer_last_name(cls, customer_last_name):
        pattern = r"^[\u0600-\u06FF ]{2,32}$"
        match = re.fullmatch(pattern, customer_last_name)
        if not match:
            raise HTTPException(status_code=422, detail={"error": "نام خانوادگی وارد شده صحیح نمیباشد"})
        return customer_last_name

    @validator("customer_postal_code")
    def validate_customer_postal_code(cls, customer_postal_code):
        pattern = r"^[0-9]{10}$"
        match = re.fullmatch(pattern, customer_postal_code)
        if not match:
            raise HTTPException(status_code=422, detail={"error": "کد پستی وارد شده صحیح نمیباشد"})
        return customer_postal_code

    @validator("customer_email")
    def validate_customer_email(cls, customer_email):
        pattern = r"^([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+$"
        match = re.fullmatch(pattern, customer_email)
        if not match:
            raise HTTPException(status_code=422, detail={"message": "لطفا ایمیل را به درستی وارد کنید"})
        return customer_email

    @validator("customer_shop_name")
    def validate_customer_shop_name(cls, customer_shop_name):
        pattern = r"^[\u0600-\u06FF ]{2,32}$"
        match = re.fullmatch(pattern, customer_shop_name)
        if not match:
            raise HTTPException(status_code=422, detail={"message": "لطفا نام فروشگاه را به درستی وارد کنید"})
        return customer_shop_name

    @validator("customer_account_number")
    def validate_customer_account_number(cls, customer_account_number):
        pattern = r"^[0-9]{7,20}$"
        match = re.fullmatch(pattern, customer_account_number)
        if not match:
            raise HTTPException(status_code=422, detail={"message": "لطفا شماره حساب خود را به درستی وارد کنید"})
        return customer_account_number

    @validator("customer_telephone_number")
    def validate_customer_telephone_number(cls, customer_telephone_number):
        pattern = r"^0[0-9]{10}$"
        match = re.fullmatch(pattern, customer_telephone_number)
        if not match:
            raise HTTPException(status_code=422, detail={"message": "لطفا تلفن ثابت خود را به درستی وارد کنید"})
        return customer_telephone_number

    @validator("customer_shop_status")
    def validate_customer_shop_status(cls, customer_shop_status):
        values = ["مالک", "استیجاری", "رهن"]
        if customer_shop_status not in values:
            raise HTTPException(status_code=422, detail={"message": "لطفا وضعیت فروشگاه را به درستی وارد کنید"})
        return customer_shop_status

    @validator("customer_shop_location")
    def validate_customer_shop_location(cls, customer_shop_location):
        values = ["داخل پاساژ", "خیابان اصلی", "خیابان فرعی"]
        if customer_shop_location not in values:
            raise HTTPException(status_code=422, detail={"message": "لطفا موقعیت مکانی فروشگاه را به درستی وارد کنید"})
        return customer_shop_location

    @validator("customer_education")
    def validate_customer_education(cls, customer_education):
        values = ["دیپلم", "کارشناسی", "کارشناسی ارشد", "دکتری"]
        if customer_education not in values:
            raise HTTPException(status_code=422, detail={"message": "لطفا تحصیلات را به درستی وارد کنید"})
        return customer_education

    @validator("customer_ofogh_code")
    def validate_customer_ofogh_code(cls, customer_ofogh_code):
        pattern = r"^[0-9]{4,5}$"
        match = re.fullmatch(pattern, customer_ofogh_code)
        if not match:
            raise HTTPException(status_code=422, detail={"message": "لطفا کد افق خود را به درستی وارد کنید"})
        return customer_ofogh_code

    @validator("customer_class")
    def validate_customer_class(cls, customer_class):
        pattern = r"^[\u0600-\u06FF]{2,32}$"
        match = re.fullmatch(pattern, customer_class)
        if not match:
            raise HTTPException(status_code=422, detail={"message": "لطفا صنف خود را به درستی وارد کنید"})
        return customer_class

    @validator("customer_shop_postal_code")
    def validate_customer_shop_postal_code(cls, customer_shop_postal_code):
        pattern = "^[0-9]{10}$"
        match = re.fullmatch(pattern, customer_shop_postal_code)
        if not match:
            raise HTTPException(status_code=422, detail={"message": "لطفا کد پستی محل کسب خود را به درستی وارد کنید"})
        return customer_shop_postal_code


# ----------------------- change password ----------------------------#
class ChangePassword(BaseModel):
    oldPassword: str = Field(
        title="رمز عبور قبلی",
        alias="customerOldPassword",
        name="customerOldPassword",
        placeholder="abcd1234ABCD",
        description="password must be string and len between 8 and 32 character",
        minLength=8,
        maxLength=32,
        dataType="string",
        type="password",
        isRquired=True,
        regexPattern=r"^([a-zA-Z0-9'!#$%&'*+/=?^_`{|}~.-]{6,32})",
    )
    newPassword: str = Field(
        title="رمز عبور جدید",
        alias="customerNewPassword",
        name="customerNewPassword",
        placeholder="abcd1234ABCD",
        description="password must be string and len between 8 and 32 character",
        minLength=8,
        maxLength=32,
        dataType="string",
        type="password",
        isRquired=True,
        regexPattern=r"^([a-zA-Z0-9'!#$%&'*+/=?^_`{|}~.-]{6,32})",
    )

    @validator("oldPassword", "newPassword")
    def validate_password(cls, code):
        pattern = r"^([a-zA-Z0-9'!#$%&'*+/=?^_`{|}~.-]{6,32})"
        match = re.fullmatch(pattern, code)
        if not match:
            raise HTTPException(status_code=422, detail={"error": "رمز وارد شده صحیح نمی باشد"})
        return code


class Delivery(BaseModel):
    deliveryFirstName: Optional[str] = Field(
        description="",
        title="نام تحویل گیرنده",
        alias="deliveryFirstName",
        name="deliveryFirstName",
        placeholder="مهدی",
        minLength=2,
        maxLength=32,
        dataType="string",
        type="text",
        regexPattern=r"^[\u0600-\u06FF ]{2,32}$",
        isRquired=False,
    )
    deliveryLastName: Optional[str] = Field(
        description="",
        alias="deliveryLastName",
        title="نام خانوادگی تحویل گیرنده",
        name="deliveryLastName",
        placeholder="مهدوی",
        minLength=2,
        maxLength=32,
        dataType="string",
        type="text",
        regexPattern=r"^[\u0600-\u06FF ]{2,32}$",
        isRquired=False,
    )
    deliveryNationalId: Optional[str] = Field(
        description="",
        title="کد ملی تحویل گیرنده",
        alias="deliveryNationalID",
        name="deliveryNationalID",
        placeholder="6150077698",
        minLength=10,
        maxLength=10,
        dataType="string",
        type="text",
        isRquired=False,
        regexPattern="^[0-9]{10}$",
    )
    deliveryMobileNumber: Optional[str] = Field(
        alias="deliveryMobileNumber",
        description="",
        title="تلفن تحویل گیرنده",
        name="deliveryMobileNumber",
        placeholder="",
        minLength=4,
        maxLength=128,
        dataType="string",
        type="text",
        isRquired=False,
    )

    @validator("deliveryMobileNumber")
    def validate_mobile_num(cls, delivery_mobile_number):
        # sourcery skip: instance-method-first-arg-name
        pattern = r"^09[0-9]{9}$"
        match = re.fullmatch(pattern, delivery_mobile_number)
        if not match:
            raise HTTPException(status_code=422, detail={"error": "شماره تلفن وارد شده صحیح نمیباشد"})
        return delivery_mobile_number

    @validator("deliveryFirstName")
    def validate_delivery_first_name(cls, delivery_first_name):
        # sourcery skip: instance-method-first-arg-name
        pattern = r"^[\u0600-\u06FF ]{2,32}$"
        match = re.fullmatch(pattern, delivery_first_name)
        if not match:
            raise HTTPException(status_code=422, detail={"error": "نام وارد شده صحیح نمیباشد"})
        return delivery_first_name

    @validator("deliveryLastName")
    def validate_delivery_lastname(cls, delivery_lastname):
        # sourcery skip: instance-method-first-arg-name
        pattern = r"^[\u0600-\u06FF ]{2,32}$"
        match = re.fullmatch(pattern, delivery_lastname)
        if not match:
            raise HTTPException(status_code=422, detail={"error": "نام خانوادگی وارد شده صحیح نمیباشد"})
        return delivery_lastname

    @validator("deliveryNationalId")
    def validate_customer_national_id(cls, delivery_national_id):
        pattern = r"^[0-9]{10}$"
        match = re.fullmatch(pattern, delivery_national_id)
        if not match:
            raise HTTPException(status_code=422, detail={"error": "کد ملی وارد شده صحیح نمیباشد"})
        if not codemelli.validator(delivery_national_id):
            raise HTTPException(status_code=422, detail={"error": "کد ملی وارد شده صحیح نمی باشد"})
        return delivery_national_id


class Person(BaseModel):
    data: dict


class GetInformal(BaseModel):
    ...
