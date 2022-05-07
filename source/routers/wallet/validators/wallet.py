import re
from pydantic import BaseModel, Field, validator


class Wallet(BaseModel):
    customer_id: int = Field(..., alias="customerId")
    customer_name: str = Field(..., alias="customerName")
    customer_phone_number: str = Field(..., alias="customerPhoneNumber")

    @validator("customer_name")
    def check_customer_name(cls, customer_name):
        if not customer_name.isalpha():
            raise ValueError("customer name must be alphabetic")
        return customer_name

    @validator("customer_phone_number")
    def check_customer_phone_number(cls, customer_phone_number):
        regex = r'^09[0-9]{9}$'
        check = re.fullmatch(regex, customer_phone_number)
        if not check:
            raise ValueError("phone number is not acceptable")
        return customer_phone_number
