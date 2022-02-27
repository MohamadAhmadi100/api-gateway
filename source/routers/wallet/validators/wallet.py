import re
from datetime import datetime
from enum import Enum

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

#
# class ActionType(str, Enum):
#     auto = "auto"
#     manual = "manual"
#
#
# class PaymentMethod(str, Enum):
#     melli = "melli"
#     mellat = "mellat"
#     saman = "saman"
#
#
# class Balance(str, Enum):
#     charge = "charge"
#     consume = "consume"
#
#
# class ProcessType(str, Enum):
#     success = "success"
#     failed = "failed"
#
#
# class Type(str, Enum):
#     rebate = "rebate"
#     return_order = "return order"
#     return_product = "return product"
#     customer_charge = "customer charge"
#     staff_charge = "staff charge"
#     customer_consume = "customer consume"
#

# class Transaction(BaseModel):
#     action_type: ActionType = Field(..., alias="actionType")
#     customer_id: int = Field(..., alias="customerId")
#     order_number: int = Field(..., alias="orderNumber")
#     payment_id: int = Field(..., alias="paymentId")
#     payment_method: PaymentMethod = Field(..., alias="paymentMethod")
#     payment_date: str = Field(..., alias="paymentDate")
#     amount: str = Field(..., alias="amount")
#     balance: Balance = Field(..., alias="balance")
#     wallet_id: int = Field(..., alias="walletId")
#     process_type: ProcessType = Field(..., alias="processType")
#     user_id: int = Field(..., alias="userId")
#     user_name: str = Field(..., alias="userName")
#     type_: Type = Field(..., alias="type")
#
#     @validator('amount')
#     def check_amount(cls, v):
#         """
#         amount should be numeric
#         """
#         if not v.isalnum():
#             raise ValueError('must be alphanumeric')
#
#         if int(v) < 10000:
#             raise ValueError("must be greater than 1000 toman")
#         return v
