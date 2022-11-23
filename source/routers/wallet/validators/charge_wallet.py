import re
from enum import Enum
from fastapi import HTTPException
from pydantic import BaseModel, Field, validator


class DeviceType(str, Enum):
    web = "web"
    android = "android"
    ios = "ios"


class Charge(BaseModel):
    amount: int = Field(..., alias="amount")
    wallet_id: int = Field(..., alias="walletId")
    customer_id: int = Field(..., alias="customerId")
    device_type: DeviceType = Field(default="web", alias="deviceType")

    @validator('amount')
    def check_amount(cls, amount):
        if amount < 1000:
            raise ValueError("must be greater than 1000 rial")
        return amount
