from fastapi import HTTPException
from enum import Enum
from pydantic import BaseModel, validator, Field


class PaymentType(Enum):
    VALUE_1 = "cheque"
    VALUE_2 = "online_payment"

class AddCredit(BaseModel):
    amount: int = Field(..., alias="amount")
    payment_type: PaymentType


class AcceptCredit(BaseModel):
    referral_number: int = Field(..., alias="referral_number")
