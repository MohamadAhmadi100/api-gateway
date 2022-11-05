from pydantic import BaseModel, Field
from typing import List, Union, Dict

class Customer(BaseModel):
    user_id: int = Field(alias="customerId")
    phone_number: str = Field(alias="customerPhoneNumber")

class Product(BaseModel):
    status : str = Field(default="initial")
    systemCode: str = Field(alias="systemCode")
    storageId: str = Field(alias="storageId")
    price: int
    totalPrice: int
    count: int
    model: str
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



