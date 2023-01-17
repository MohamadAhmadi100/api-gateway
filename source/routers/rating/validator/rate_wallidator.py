from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field


class SortType(str, Enum):
    ascend = "ascend"
    descend = "descend"


class LikesParameters(str, Enum):
    likes = "likes"
    dislikes = "dislikes"


class SubDetails(BaseModel):
    negative: List[str] = Field(None, alias="negative")
    positive: List[str] = Field(None, alias="positive")
    description: str = Field(None, alias="description")

    def get_sub_details(self):
        return {
            "negative": list(self.negative),
            "positive": list(self.positive),
            "description": str(self.description),
        }



class DetailsType(BaseModel):
    comments: Optional[SubDetails] = Field(None, alias="comments")
    rate: dict = Field(None, alias="rate")
    average: float = Field(..., alias="average")

    def get_details_type(self):
        return {
            "comments": dict(self.comments.get_sub_details()),
            "rate": dict(self.rate),
            "average": float(self.average),
        }


class Details(BaseModel):
    product: Optional[DetailsType] = Field(..., alias="product")
    seller: Optional[DetailsType] = Field(..., alias="seller")

    def get_details(self):
        return {
            "product": dict(self.product.get_details_type()),
            "seller": dict(self.seller.get_details_type())
        }


class InsertRate(BaseModel):

    system_code: str = Field(..., alias="systemCode")
    sku: str = Field(..., alias="sku")
    customer_id: int = Field(..., alias="customerId")
    customer_name: str = Field(..., alias="customerName")
    customer_type: str = Field(..., alias="customerType")
    seller_id: int = Field(..., alias="sellerId")
    seller_name: str = Field(..., alias="sellerName")
    details: Optional[Details] = Field(..., alias="details")

    def get_insert_rate(self):
        return {
            "system_code": self.system_code,
            "sku": self.sku,
            "customer_id": self.customer_id,
            "customer_name": self.customer_name,
            "customer_type": self.customer_type,
            "seller_id": self.seller_id,
            "seller_name": self.seller_name,
            "details": self.details.get_details(),
        }
