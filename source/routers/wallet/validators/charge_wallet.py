import re

from fastapi import HTTPException
from pydantic import BaseModel, Field, validator


class Charge(BaseModel):
    amount: int = Field(..., alias="amount", isRequired=True)
    bank_name: str = Field(..., alias="bankName", isRequired=True)
    customer_id: str = Field(..., alias="customerId", isRequired=True)
    action_type: str = Field(..., alias="actionType")
    payment_method: str = Field(..., alias="paymentMethod")
    balance: str = Field(..., alias="balance")
    wallet_id: str = Field(..., alias="walletId")
    process_type: str = Field(..., alias="processType")
    type: str = Field(..., alias="type")





