from pydantic import BaseModel, Field, validator
from typing import List, Union, Dict
from fastapi import HTTPException

class Customer(BaseModel):
    user_id: int = Field(alias="customerId")
    phone_number: str = Field(alias="customerPhoneNumber")

class Product(BaseModel):
    status : str = Field(default="initial")
    systemCode: str = Field(alias="systemCode")
    storageId: str = Field(alias="storageId")
    price: int = Field(alias="price")
    totalPrice: int = Field(alias="totalPrice")
    count: int
    model: dict
    name: str
    brand: dict
    color: dict
    guarantee: dict
    seller: dict
    category: dict
    imeis: List[str]


class SellRequest(BaseModel):
    customer: Union[Customer]
    products: Union[List[Product], list]
    device_type: str = Field(alias="deviceType")
    payment_type: str = Field(alias="paymentType")

    @validator('payment_type')
    def validate_payment_type(cls, payment_type):
        if payment_type not in ['aiBanking', 'cashondelivery']:
            raise HTTPException(status_code=422, detail={"error": "نوع متد پرداخت معتبر نیست"})
        return payment_type



