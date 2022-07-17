from pydantic import BaseModel, Field
from typing import List, Union


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
    products: Union[List[Product], list] = Field(alias="products")
    shipment: dict = Field(alias="shipment")
    storage_id: str = Field(alias="storageId")