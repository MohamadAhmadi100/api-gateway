from pydantic import BaseModel, Field
from typing import List, Union, Optional


# class Product(BaseModel):
#     parent_system_code: str = Field(alias="parentSystemCode")
#     system_code: str = Field(alias="systemCode")
#     brand: str
#     model: str
#     name: str
#     color: str
#     guarantee: str
#     seller: str
#     price: int
#     count: int
#     imei_flag: Optional[bool] = Field(alias="imeiFlag", default=False)




class RequestGoods(BaseModel):
    products: List[dict] = Field(alias="products")
    shipment: dict = Field(alias="shipment")
    storage_id: str = Field(alias="storageId")