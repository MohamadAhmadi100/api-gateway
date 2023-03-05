from pydantic import BaseModel, Field
from typing import List, Union




class Product(BaseModel):
    systemCode: str
    storageId: str
    storageLabel: str
    count: int
    price: int
    model: dict
    name: str
    brand: dict
    color: dict
    guarantee: dict
    seller: dict
    mainCategory: dict
    subCategory: dict
    attributes: list
    imeiFlag: bool
    imeis: List[str]




class Return(BaseModel):
    products: Union[List[Product], list]

