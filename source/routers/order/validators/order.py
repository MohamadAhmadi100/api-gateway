from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel, Field, validator


class BaseCart(BaseModel):
    pass


class wallet(BaseModel):
    wallet_amount: int


class payment(BaseModel):
    payment_method: str

    @validator("payment_method")
    def payment_method_validator(cls, value):
        allowed_values = ['cashondelivery', 'aiBanking', 'deposit']
        if not isinstance(value, str):
            raise HTTPException(status_code=400, detail="payment method must be a string")
        if value not in allowed_values:
            raise HTTPException(status_code=400, detail=f"payment must be one of {allowed_values}")
        return value


class informal(BaseModel):
    national_id: str


class cancel(BaseModel):
    orderNumber: int


class edit_order_validator(BaseModel):
    orderNumber: int
    customerId: int
    customerType: str
    customerFullName: str
    edit_list: list = Field(default=[{
        "systemCode": "",
        "storageId": "",
        "oldCount": "",
        "newCount": "",
        "sku": ""
    }])

    @validator("edit_list")
    def edit_list_validator(cls, value):
        allowed_keys = ["systemCode", "storageId", "newCount", "oldCount", "sku"]
        for items in value:
            for k, v in items.items():
                if k not in allowed_keys:
                    raise HTTPException(status_code=400, detail=f"edit list must be one of {allowed_keys}")
        return value
