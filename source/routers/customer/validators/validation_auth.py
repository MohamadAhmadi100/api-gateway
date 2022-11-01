import re
from enum import Enum
from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel, validator, Field


class CustomerType(str, Enum):
    B2B = "B2B"
    B2C = "B2C"


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
    customer_type: Optional[CustomerType] = Field(
        alias="customerType",
        description="",
        title="نوع مشتری",
        name="customerType",
        minLength=1,
        maxLength=4,
        dataType="string",
        type="hidden",
        regexPattern="",
        isRquired=False,
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
        regexPattern="^([a-zA-Z0-9'!#$%&'*+/=?^_`{|}~.-]{6,32})",
    )
    customer_type: Optional[CustomerType] = Field(
        alias="customerType",
        description="",
        title="نوع مشتری",
        name="customerType",
        minLength=1,
        maxLength=4,
        dataType="string",
        type="hidden",
        regexPattern="",
        isRquired=False,
    )

    @validator("customer_password")
    def validate_password(cls, code):
        pattern = r"^([a-zA-Z0-9'!#$%&'*+/=?^_`{|}~.-]{6,32})"
        match = re.fullmatch(pattern, code)
        if not match:
            raise HTTPException(status_code=422, detail={"error": "رمز وارد شده صحیح نمی باشد"})
        return code


class CustomerForgetPassword(BaseModel):
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
        regexPattern=r"^([a-zA-Z0-9'!#$%&'*+/=?^_`{|}~.-]{6,32})",
    )

    @validator("customer_password")
    def validate_password(cls, code):
        pattern = r"^([a-zA-Z0-9'!#$%&'*+/=?^_`{|}~.-]{6,32})"
        match = re.fullmatch(pattern, code)
        if not match:
            raise HTTPException(status_code=422, detail={"error": "رمز وارد شده صحیح نمی باشد"})
        return code
