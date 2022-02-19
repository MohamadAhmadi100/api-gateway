from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, validator


class Wallet(BaseModel):
    customer_id: int = Field(alias="customerId")


class ActionType(str, Enum):
    auto = "auto"
    manual = "manual"


class PaymentMethod(str, Enum):
    melli = "melli"
    mellat = "mellat"
    saman = "saman"


class Balance(str, Enum):
    charge = "charge"
    consume = "consume"


class ProcessType(str, Enum):
    success = "success"
    failed = "failed"


class Type(str, Enum):

    rebate = "rebate"
    return_order = "return order"
    return_product = "return product"
    customer_charge = "customer charge"
    staff_charge = "staff charge"
    customer_consume = "customer consume"


class Transaction(BaseModel):
    action_type: ActionType = Field(..., alias="actionType")
    customer_id: int = Field(..., alias="customerId")
    order_number: int = Field(..., alias="orderNumber")
    payment_id: int = Field(..., alias="paymentId")
    payment_method: PaymentMethod = Field(..., alias="paymentMethod")
    payment_date: datetime = Field(..., alias="paymentDate")
    amount: str = Field(..., alias="amount")
    balance: Balance = Field(..., alias="balance")
    wallet_id: int = Field(..., alias="walletId")
    process_type: ProcessType = Field(..., alias="processType")
    user_id: int = Field(..., alias="userId")
    user_name: str = Field(..., alias="userName")
    type_: Type = Field(..., alias="type")

    @validator('amount')
    def check_amount(cls, v):
        """
        amount should be numeric
        """
        if not v.isalnum():
            raise ValueError('must be alphanumeric')

        if int(v) < 10000:
            raise ValueError("must be greater than 1000 toman")
        return v
