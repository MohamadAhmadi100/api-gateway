from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field


class SortType(str, Enum):
    ascend = "ascend"
    descend = "descend"


class SubDetails(BaseModel):
    negative: List[str] = Field(None, alias="negative")
    positive: List[str] = Field(None, alias="positive")
    description: str = Field(None, alias="description")


class Properties(BaseModel):
    product_property: List[dict] = Field(None, alias="productProperty")
    seller_property: List[dict] = Field(None, alias="sellerProperty")


class Details(BaseModel):
    product_details: Optional[SubDetails] = Field(None, alias="productDetails")
    seller_details: Optional[SubDetails] = Field(None, alias="sellerDetails")


class InsertRate(BaseModel):
    system_code: str = Field(None, alias="systemCode")
    sku: str = Field(None, alias="sku")
    customer_id: int = Field(..., alias="customerId")
    customer_name: str = Field(..., alias="customerName")
    customer_type: str = Field(..., alias="customerType")
    seller_id: int = Field(None, alias="sellerId")
    seller_name: int = Field(None, alias="sellerName")
    details: Optional[Details] = Field(None, alias="details")
    properties: Optional[Properties] = Field(None, alias="properties")


