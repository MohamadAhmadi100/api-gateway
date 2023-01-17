from pydantic import BaseModel, Field
from typing import List, Union, Optional, Dict

class Attribute(BaseModel):
    name: str
    ecommerce_use_in_filter: bool
    ecommerce_use_in_search: bool
    editable_in_ecommerce: bool
    editable_in_portal: bool
    label: str
    portal_use_in_filter: bool
    portal_use_in_search: bool
    show_in_ecommerce: bool
    show_in_portal: bool
    value: Optional[str] = None


class Product(BaseModel):
    system_code: str = Field(alias="systemCode")
    storage_id: str = Field(alias="storageId")
    price: int
    count: int
    model: dict
    name: str
    brand: dict
    color: dict
    guarantee: dict
    seller: dict
    main_category: dict = Field(alias="mainCategory")
    sub_category: dict = Field(alias="subCategory")
    attributes: Union[List[Attribute], list]
    imeis: list

class IMEI(BaseModel):
    product: Product
    customer_id: str = Field(alias="customerId")
    referral_number: str = Field(alias="referralNumber")