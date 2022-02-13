import re

from fastapi import HTTPException
from pydantic import BaseModel, validator, Field

"""
handling generate form(mobile number) validations on frontend side &&& validation data on backend Side
"""


class CustomerAuth(BaseModel):
    # generate frontend validation form
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
        isRquired=True,
        regexPattern="^09[0-9]{9}$",
    )

    # validation phone number on backend side
    # TODO validate code type

    @validator("customer_phone_number")
    def validate_phone_num(cls, phone_number):
        pattern = r"^09[0-9]{9}$"
        match = re.fullmatch(pattern, phone_number)
        if not match:
            raise HTTPException(status_code=422, detail={"error": "شماره موبایل به درستی وارد نشده است"})
        return phone_number


class CustomerVerifyOTP(CustomerAuth):
    customer_code: str = Field(
        title="رمز یک بار مصرف",
        description="otp code must be string and len 4 character",
        name="customerCode",
        alias="customerCode",
        placeholder="4563",
        minLength=4,
        maxLength=4,
        dataType="string",
        type="text",
        isRequired=True,
        regexPattern="^[0-9]{4}$",
    )

    @validator("customer_code")
    def validate_otp(cls, code):
        pattern = r"^[0-9]{4}$"
        match = re.fullmatch(pattern, code)
        if not match:
            raise HTTPException(status_code=422, detail={"error": "کد وارد نشده صحیح نمی باشد"})
        return code


class CustomerVerifyPassword(CustomerAuth):
    customer_password: str = Field(
        title="رمز عبور",
        alias="customerPassword",
        name="customerPassword",
        placeholder="qwer1234QWER",
        description="password must be string and len between 8 and 32 character",
        minLength=8,
        maxLength=32,
        dataType="string",
        type="password",
        isRquired=True,
        regexPattern="^^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9]).{8,32}$",
    )

    @validator("customer_password")
    def validate_password(cls, code):
        pattern = r"^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9]).{8,32}$"
        match = re.fullmatch(pattern, code)
        if not match:
            raise HTTPException(status_code=422, detail={"error": "رمز وارد شده صحیح نمی باشد"})
        return code
