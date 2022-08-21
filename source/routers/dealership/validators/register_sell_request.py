from pydantic import BaseModel, Field
from typing import List, Union, Optional



class Product(BaseModel):
    parent_system_code: str = Field(alias="parentSystemCode")
    system_code: str = Field(alias="systemCode")
    brand: str
    model: str
    name: str
    color: str
    guarantee: str
    price: int
    imei: str


class SellRequest(BaseModel):
    first_name: str = Field(alias="firstName")
    last_name: str = Field(alias="lastName")
    customer_code: str = Field(alias="customerCode")
    phone_number: str = Field(alias="phoneNumber")
    postal_code: str = Field(alias="postalCode")
    insurance_request: str = Field(alias="insuranceRequest")
    address: str = Field(alias="address")
    products: Union[List[Product], list] = Field(alias="products")



