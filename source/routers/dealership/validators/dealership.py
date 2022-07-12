from pydantic import BaseModel, Field
from typing import List


class Product(BaseModel):
    system_code: str
    brand: str
    model: str
    name: str
    color: str
    guarantee: str
    seller: str
    price: int
    count: int




class RequestGoods(BaseModel):
    products: List[Product] = Field(alias="products")
    shipment: dict = Field(alias="shipment")
    storage_id: str = Field(alias="storageId")