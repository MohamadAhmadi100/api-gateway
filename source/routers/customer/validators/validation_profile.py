import re
from typing import Optional
from source.helpers.create_class import CreateClass
from fastapi import HTTPException
from pydantic import BaseModel, validator, Field
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
    data: dict
    # customer_first_name: Optional[str] = Field(
    #     description="",
    #     title="نام",
    #     alias="customerFirstName",
    #     name="customerFirstName",
    #     placeholder="مهدی",
    #     minLength=2,
    #     maxLength=32,
    #     dataType="string",
    #     type="text",
    #     regexPattern=r"^[\u0600-\u06FF ]{2,32}$",
    #     isRquired=False,
    # )
    # customer_last_name: Optional[str] = Field(
    #     description="",
    #     alias="customerLastName",
    #     title="نام خانوادگی",
    #     name="customerLastName",
    #     placeholder="مهدوی",
    #     minLength=2,
    #     maxLength=32,
    #     dataType="string",
    #     type="text",
    #     regexPattern=r"^[\u0600-\u06FF ]{2,32}$",
    #     isRquired=False,
    # )
    # customer_national_id: Optional[str] = Field(
    #     description="",
    #     title="کد ملی",
    #     alias="customerNationalID",
    #     name="customerNationalID",
    #     placeholder="6150077698",
    #     minLength=10,
    #     maxLength=10,
    #     dataType="string",
    #     type="text",
    #     isRquired=False,
    #     regexPattern="^[0-9]{10}$",
    # )
    # customer_region_code: Optional[str] = Field(
    #     description="",
    #     alias="customerRegionCode",
    #     title="",
    #     name="customerRegionCode",
    #     minLength=1,
    #     maxLength=8,
    #     dataType="string",
    #     type="hidden",
    #     regexPattern=r"^[a-z,0-9,A-Z]{2,8}$",
    #     isRquired=False,
    # )
    # customer_city: Optional[str] = Field(
    #     alias="customerCity",
    #     description="",
    #     title="نام شهر",
    #     name="customerCity",
    #     placeholder="تهران",
    #     minLength=2,
    #     maxLength=32,
    #     dataType="string",
    #     type="text",
    #     regexPattern=r"^[\u0600-\u06FF ]{2,32}$",
    #     isRquired=False,
    # )
    # customer_city_id: Optional[str] = Field(
    #     alias="customerCityID",
    #     description="",
    #     title="ای دی شهر",
    #     name="customerCityID",
    #     minLength=1,
    #     maxLength=4,
    #     dataType="string",
    #     type="hidden",
    #     regexPattern="^[0-9]{1,4}$",
    #     isRquired=False,
    # )
    # customer_province: Optional[str] = Field(
    #     alias="customerProvince",
    #     description="",
    #     title="استان",
    #     name="customerProvince",
    #     placeholder="تهران",
    #     minLength=2,
    #     maxLength=32,
    #     dataType="string",
    #     type="text",
    #     regexPattern=r"^[\u0600-\u06FF ]{2,32}$",
    #     isRquired=False,
    # )
    # customer_province_id: Optional[str] = Field(
    #     alias="customerProvinceID",
    #     description="",
    #     title="ای دی استان",
    #     name="customerProvinceID",
    #     minLength=1,
    #     maxLength=4,
    #     dataType="string",
    #     type="hidden",
    #     regexPattern="^[0-9]{1,4}$",
    #     isRquired=False,
    # )
    # customer_address: Optional[str] = Field(
    #     alias="customerAddress",
    #     description="",
    #     title="آدرس",
    #     name="customerAddress",
    #     placeholder="تهران پلاک ۳",
    #     minLength=4,
    #     maxLength=128,
    #     dataType="string",
    #     type="text",
    #     regexPattern=r"^[\u0600-\u06FF - , - ، ]{4,128}$",
    #     isRquired=False,
    # )
    #
    # customer_postal_code: Optional[str] = Field(
    #     alias="customerPostalCode",
    #     description="",
    #     title="کد پستی",
    #     name="customerPostalCode",
    #     placeholder="4571915113",
    #     minLength=10,
    #     maxLength=10,
    #     dataType="string",
    #     type="text",
    #     regexPattern="^[0-9]{10}$",
    #     isRquired=False,
    # )
    # customer_email: Optional[str] = Field(
    #     alias="customerEmail",
    #     description="",
    #     title="پست الکترونیک",
    #     name="customerEmail",
    #     placeholder="example@me.com",
    #     minLength=4,
    #     maxLength=128,
    #     dataType="string",
    #     type="text",
    #     regexPattern=r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
    #     isRquired=False,
    # )
    # customer_shop_name: Optional[str] = Field(
    #     alias="customerShopName",
    #     description="",
    #     title="نام شرکت/مغازه",
    #     name="customerShopName",
    #     placeholder="",
    #     minLength=4,
    #     maxLength=128,
    #     dataType="string",
    #     type="text",
    #     regexPattern=r"^[\u0600-\u06FF ]{2,32}$",
    #     isRquired=False,
    # )
    # customer_account_number: Optional[str] = Field(
    #     alias="customerAccountNumber",
    #     description="",
    #     title="شماره حساب",
    #     name="customerAccountNumber",
    #     placeholder="",
    #     minLength=4,
    #     maxLength=128,
    #     dataType="string",
    #     type="text",
    #     isRquired=False,
    # )
    # customer_telephone_number: Optional[str] = Field(
    #     alias="customerTelephoneNumber",
    #     description="",
    #     title="تلفن ثابت",
    #     name="customerTelephoneNumber",
    #     placeholder="",
    #     minLength=4,
    #     maxLength=128,
    #     dataType="string",
    #     type="text",
    #     isRquired=False,
    # )
    # customer_shop_status: Optional[str] = Field(
    #     alias="customerShopStatus",
    #     description="",
    #     title="وضعیت فروشگاه",
    #     name="customerShopStatus",
    #     placeholder="",
    #     minLength=2,
    #     maxLength=32,
    #     dataType="string",
    #     type="text",
    #     isRquired=False,
    # )
    # customer_shop_location: Optional[str] = Field(
    #     alias="customerShopLocation",
    #     description="",
    #     title="موقعیت مکانی فروشگاه",
    #     name="customerShopLocation",
    #     placeholder="",
    #     minLength=2,
    #     maxLength=32,
    #     dataType="string",
    #     type="text",
    #     isRquired=False,
    # )
    # customer_education: Optional[str] = Field(
    #     alias="customerEducation",
    #     description="",
    #     title="تحصیلات",
    #     name="customerEducation",
    #     placeholder="",
    #     minLength=2,
    #     maxLength=32,
    #     dataType="string",
    #     type="text",
    #     isRquired=False,
    # )
    # attributes: dict
    #
    # @validator("customer_first_name")
    # def validate_customer_first_name(cls, customer_first_name):
    #     pattern = r"^[\u0600-\u06FF ]{2,32}$"
    #     match = re.fullmatch(pattern, customer_first_name)
    #     if not match:
    #         raise HTTPException(status_code=422, detail={"error": "نام وارد شده صحیح نمیباشد"})
    #     return customer_first_name
    #
    # @validator("customer_last_name")
    # def validate_customer_last_name(cls, customer_last_name):
    #     pattern = r"^[\u0600-\u06FF ]{2,32}$"
    #     match = re.fullmatch(pattern, customer_last_name)
    #     if not match:
    #         raise HTTPException(status_code=422, detail={"error": "نام خانوادگی وارد شده صحیح نمیباشد"})
    #     return customer_last_name
    #
    # @validator("customer_national_id")
    # def validate_customer_national_id(cls, customer_national_id):
    #     pattern = r"^[0-9]{10}$"
    #     match = re.fullmatch(pattern, customer_national_id)
    #     if not match:
    #         raise HTTPException(status_code=422, detail={"error": "کد ملی وارد شده صحیح نمیباشد"})
    #     return customer_national_id
    #
    # @validator("customer_city")
    # def validate_customer_city(cls, customer_city):
    #     pattern = r"^[\u0600-\u06FF ]{2,32}$"
    #     match = re.fullmatch(pattern, customer_city)
    #     if not match:
    #         raise HTTPException(status_code=422, detail={"error": "شهر وارد شده صحیح نمیباشد"})
    #     return customer_city
    #
    # @validator("customer_province")
    # def validate_customer_province(cls, customer_province):
    #     pattern = r"^[\u0600-\u06FF ]{2,32}$"
    #     match = re.fullmatch(pattern, customer_province)
    #     if not match:
    #         raise HTTPException(status_code=422, detail={"error": "استان وارد شده صحیح نمیابشد"})
    #     return customer_province
    #
    # @validator("customer_address")
    # def validate_customer_address(cls, customer_address):
    #     pattern = r"^[\u0600-\u06FF - , - ، ]{4,128}$"
    #     match = re.fullmatch(pattern, customer_address)
    #     if not match:
    #         raise HTTPException(status_code=422, detail={"error": "آدرس وارد شده صحیح نمیباشد"})
    #     return customer_address
    #
    # @validator("customer_postal_code")
    # def validate_customer_postal_code(cls, customer_postal_code):
    #     pattern = r"^[0-9]{10}$"
    #     match = re.fullmatch(pattern, customer_postal_code)
    #     if not match:
    #         raise HTTPException(status_code=422, detail={"error": "کد پستی وارد شده صحیح نمیباشد"})
    #     return customer_postal_code
    #
    # @validator("customer_province_id")
    # def validate_customer_province_id(cls, customer_province_id):
    #     pattern = r"^[0-9]{1,8}$"
    #     match = re.fullmatch(pattern, customer_province_id)
    #     if not match:
    #         raise HTTPException(status_code=422, detail={"error": "شناسه استان وارد شده صحیح نمیباشد"})
    #     return customer_province_id
    #
    # @validator("customer_region_code")
    # def validate_customer_region_code(cls, customer_region_code):
    #     pattern = r"^[a-z,0-9,A-Z]{2,32}$"
    #     match = re.fullmatch(pattern, customer_region_code)
    #     if not match:
    #         raise HTTPException(status_code=422, detail={"error": "کد ریجن وارد شده صحیح نمیابشد"})
    #     return customer_region_code
    #
    # @validator("customer_city_id")
    # def validate_customer_city_id(cls, customer_city_id):
    #     pattern = r"^[0-9]{1,8}$"
    #     match = re.fullmatch(pattern, customer_city_id)
    #     if not match:
    #         raise HTTPException(status_code=422, detail={"error": "شناسه شهر وارد شده صحیح نمیباشد"})
    #     return customer_city_id
    #
    # @validator("customer_email")
    # def validate_customer_email(cls, customer_email):
    #     pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    #     match = re.fullmatch(pattern, customer_email)
    #     if not match:
    #         raise HTTPException(status_code=422, detail={"message": "لطفا پست الکترونیک را به درستی وارد کنید"})
    #     return customer_email
    #
    # @validator("customer_shop_name")
    # def validate_customer_shop_name(cls, customer_shop_name):
    #     pattern = r"^[\u0600-\u06FF ]{2,32}$"
    #     match = re.fullmatch(pattern, customer_shop_name)
    #     if not match:
    #         raise HTTPException(status_code=422, detail={"message": "لطفا نام فروشگاه را به درستی وارد کنید"})
    #     return customer_shop_name
    #
    # @validator("customer_shop_status")
    # def validate_customer_shop_status(cls, customer_shop_status):
    #     values = ["owner", "rent", "mortgage"]
    #     if customer_shop_status not in values:
    #         raise HTTPException(status_code=422, detail={"message": "لطفا وضعیت فروشگاه را به درستی وارد کنید"})
    #     return customer_shop_status
    #
    # @validator("customer_shop_location")
    # def validate_customer_shop_location(cls, customer_shop_location):
    #     values = ["passage", "street"]
    #     if customer_shop_location not in values:
    #         raise HTTPException(status_code=422, detail={"message": "لطفا موقعیت مکانی فروشگاه را به درستی وارد کنید"})
    #     return customer_shop_location
    #
    # @validator("customer_education")
    # def validate_customer_education(cls, customer_education):
    #     values = ["diploma", "postgraduate", "bachelor", "master", "doctorate"]
    #     if customer_education not in values:
    #         raise HTTPException(status_code=422, detail={"message": "لطفا تحصیلات را به درستی وارد کنید"})
    #     return customer_education


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
        regexPattern="^^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9]).{8,32}$",
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
        regexPattern="^^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9]).{8,32}$",
    )

    @validator("oldPassword", "newPassword")
    def validate_password(cls, code):
        pattern = r"^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9]).{8,32}$"
        match = re.fullmatch(pattern, code)
        if not match:
            raise HTTPException(status_code=422, detail={"error": "رمز وارد شده صحیح نمی باشد"})
        return code


class Delivery(BaseModel):
    delivery_first_name: str = Field(
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
    delivery_last_name: str = Field(
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
    delivery_national_id: str = Field(
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
    delivery_mobile_number: str = Field(
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
