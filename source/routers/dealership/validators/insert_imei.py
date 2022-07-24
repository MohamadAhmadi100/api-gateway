from pydantic import BaseModel, Field
from typing import List, Union, Optional



class Product(BaseModel):
    system_code: str = Field(alias="systemCode")
    brand: str
    model: str
    name: str
    color: str
    guarantee: str
    seller: str
    price: int
    count: int
    imeis: Union[List, str]
    imei_flag: Optional[bool] = Field(alias="imeiFlag", default=False)




class IMEI(BaseModel):
    product: Union[Product, dict] = Field(alias="product")
    customer_id: str = Field(alias="customerId")
    referral_number: str = Field(alias="referralNumber")