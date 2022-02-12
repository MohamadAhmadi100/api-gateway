import re
from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel, Field
from pydantic import validator


class CustomerRegister(BaseModel):
    customer_phone_number: str = Field(
        title="شماره موبایل",
        alias="customerPhoneNumber",
        name="customerPhoneNumber",
        placeholder="09371654426",
        description="phone number must be string and len 11 character",
        minLength=11,
        maxLength=11,
        dataType="string",
        type="tel",
        regexPattern="^09[0-9]{9}$",
        isRquired=True,
    )
    customer_first_name: str = Field(
        description="",
        title="نام",
        alias="customerFirstName",
        name="customerFirstName",
        placeholder="مهدی",
        minLength=2,
        maxLength=32,
        dataType="string",
        type="text",
        regexPattern=r"^[\u0600-\u06FF ]{2,32}$",
        isRquired=True,
    )
    customer_last_name: str = Field(
        description="",
        alias="customerLastName",
        title="نام خانوادگی",
        name="customerLastName",
        placeholder="مهدوی",
        minLength=2,
        maxLength=32,
        dataType="string",
        type="text",
        regexPattern=r"^[\u0600-\u06FF ]{2,32}$",
        isRquired=True,
    )
    customer_national_id: str = Field(
        description="",
        title="کد ملی",
        alias="customerNationalID",
        name="customerNationalID",
        placeholder="6150077698",
        minLength=10,
        maxLength=10,
        dataType="string",
        type="text",
        isRquired=True,
        regexPattern="^[0-9]{10}$",
    )
    customer_region_code: Optional[str] = Field(
        description="",
        alias="customerRegionCode",
        title="",
        name="customerRegionCode",
        minLength=1,
        maxLength=8,
        dataType="string",
        type="hidden",
        regexPattern=r"^[a-z,0-9,A-Z]{2,8}$",
        isRquired=False,
    )
    customer_city: str = Field(
        alias="customerCity",
        description="",
        title="نام شهر",
        name="customerCity",
        placeholder="تهران",
        minLength=2,
        maxLength=32,
        dataType="string",
        type="text",
        regexPattern=r"^[\u0600-\u06FF ]{2,32}$",
        isRquired=True,
    )
    customer_city_id: str = Field(
        alias="customerCityID",
        description="",
        title="ای دی شهر",
        name="customerCityID",
        minLength=1,
        maxLength=4,
        dataType="string",
        type="hidden",
        regexPattern="^[0-9]{1,4}$",
        isRquired=True,
    )
    customer_province: str = Field(
        alias="customerProvince",
        description="",
        title="استان",
        name="customerProvince",
        placeholder="تهران",
        minLength=2,
        maxLength=32,
        dataType="string",
        type="text",
        regexPatternr=r"^[\u0600-\u06FF ]{2,32}$",
        isRquired=True,
    )
    customer_province_id: str = Field(
        alias="customerProvinceID",
        description="",
        title="ای دی استان",
        name="customerProvinceID",
        minLength=1,
        maxLength=4,
        dataType="string",
        type="hidden",
        regexPattern="^[0-9]{1,4}$",
        isRquired=True,
    )
    customer_address: Optional[str] = Field(
        alias="customerAddress",
        description="",
        title="آدرس",
        name="customerAddress",
        placeholder="تهران پلاک ۳",
        minLength=4,
        maxLength=128,
        dataType="string",
        type="text",
        regexPattern=r"^[\u0600-\u06FF - , - ، ]{4,128}$",
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

    customer_password: Optional[str] = Field(
        title="رمز عبور",
        alias="customerPassword",
        name="customerPassword",
        placeholder="qwer1234QWER",
        description="password must be string and len between 8 and 32 character",
        minLength=8,
        maxLength=32,
        dataType="string",
        type="password",
        isRquired=False,
        regexPattern="^^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9]).{8,32}$",
    )

    customer_verify_password: Optional[str] = Field(
        title="تکرار رمز عبور",
        alias="customerVerifyPassword",
        name="customerVerifyPassword",
        placeholder="qwer1234QWER",
        description="password must be string and len between 8 and 32 character",
        minLength=8,
        maxLength=32,
        dataType="string",
        type="password",
        isRquired=False,
        regexPattern="^^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9]).{8,32}$",
    )

    @validator("customer_password")
    def validate_password(cls, verify_password):
        pattern = r"^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9]).{8,32}$"
        match = re.fullmatch(pattern, verify_password)
        if not match:
            raise HTTPException(status_code=422, detail={"error": "رمز عبور وارد شده صحیح نمی باشد"})
        return verify_password

    @validator("customer_verify_password")
    def validate_verify_password(cls, verify_password):
        pattern = r"^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9]).{8,32}$"
        match = re.fullmatch(pattern, verify_password)
        if not match:
            raise HTTPException(status_code=422, detail={"error": "تکرار رمز عبور وارد شده صحیح نمی باشد"})
        return verify_password

    @validator("customer_phone_number")
    def validate_phone_num(cls, customer_phone_number):
        pattern = r"^09[0-9]{9}$"
        match = re.fullmatch(pattern, customer_phone_number)
        if not match:
            raise HTTPException(status_code=422, detail={"error": "شماره تلفن وارد شده صحیح نمیباشد"})
        return customer_phone_number

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

    @validator("customer_national_id")
    def validate_customer_national_id(cls, customer_national_id):
        pattern = r"^[0-9]{10}$"
        match = re.fullmatch(pattern, customer_national_id)
        if not match:
            raise HTTPException(status_code=422, detail={"error": "کد ملی وارد شده صحیح نمیباشد"})
        return customer_national_id

    @validator("customer_city")
    def validate_customer_city(cls, customer_city):
        pattern = r"^[\u0600-\u06FF ]{2,32}$"
        match = re.fullmatch(pattern, customer_city)
        if not match:
            raise HTTPException(status_code=422, detail={"error": "شهر وارد شده صحیح نمیباشد"})
        return customer_city

    @validator("customer_province")
    def validate_customer_province(cls, customer_province):
        pattern = r"^[\u0600-\u06FF ]{2,32}$"
        match = re.fullmatch(pattern, customer_province)
        if not match:
            raise HTTPException(status_code=422, detail={"error": "استان وارد شده صحیح نمیابشد"})
        return customer_province

    @validator("customer_address")
    def validate_customer_address(cls, customer_address):
        pattern = r"^[\u0600-\u06FF - , - ، ]{4,128}$"
        match = re.fullmatch(pattern, customer_address)
        if not match:
            raise HTTPException(status_code=422, detail={"error": "آدرس وارد شده صحیح نمیباشد"})
        return customer_address

    @validator("customer_postal_code")
    def validate_customer_postal_code(cls, customer_postal_code):
        pattern = r"^[0-9]{10}$"
        match = re.fullmatch(pattern, customer_postal_code)
        if not match:
            raise HTTPException(status_code=422, detail={"error": "کد پستی وارد شده صحیح نمیباشد"})
        return customer_postal_code

    @validator("customer_province_id")
    def validate_customer_province_id(cls, customer_province_id):
        pattern = r"^[0-9]{1,8}$"
        match = re.fullmatch(pattern, customer_province_id)
        if not match:
            raise HTTPException(status_code=422, detail={"error": "شناسه استان وارد شده صحیح نمیباشد"})
        return customer_province_id

    @validator("customer_region_code")
    def validate_customer_region_code(cls, customer_region_code):
        pattern = r"^[a-z,0-9,A-Z]{2,32}$"
        match = re.fullmatch(pattern, customer_region_code)
        if not match:
            raise HTTPException(status_code=422, detail={"error": "کد ریجن وارد شده صحیح نمیابشد"})
        return customer_region_code

    @validator("customer_city_id")
    def validate_customer_city_id(cls, customer_city_id):
        pattern = r"^[0-9]{1,8}$"
        match = re.fullmatch(pattern, customer_city_id)
        if not match:
            raise HTTPException(status_code=422, detail={"error": "شناسه شهر وارد شده صحیح نمیباشد"})
        return customer_city_id

