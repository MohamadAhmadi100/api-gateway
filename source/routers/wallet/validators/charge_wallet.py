import re

from fastapi import HTTPException
from pydantic import BaseModel, Field, validator


class Charge(BaseModel):
    amount: int = Field(..., alias="amount")
    wallet_id: int = Field(..., alias="walletId")
    customer_id: int = Field(..., alias="customerId")

    @validator('amount')
    def check_amount(cls, amount):
        if amount < 1000:
            raise ValueError("must be greater than 1000 rial")
        return amount
