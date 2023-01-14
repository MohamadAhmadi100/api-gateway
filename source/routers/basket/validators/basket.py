from enum import Enum
from typing import List, Optional

from fastapi import HTTPException
from pydantic import BaseModel, validator, Field


class SortType(str, Enum):
    asc = "ascend"
    desc = "descend"


class SortName(str, Enum):
    basketId = "basketId"
    basketJalaliCreateTime = "basketJalaliCreateTime"
    basketJalaliStartDate = "basketJalaliStartDate"
    basketJalaliEndDate = "basketJalaliEndDate"


class BaseCart(BaseModel):
    pass


class Cart(BaseCart):
    user_info: dict = Field(..., alias="userInfo")
    # status: str = "in_cart"


class Product(BaseModel):
    systemCode: str = Field(
        title="انبار",
        alias="systemCode",
        name="systemCode",
        description="system Code ",
        dataType="str",
        type="system_code",
        isRequired=True
    )
    quantity: int = Field(
        title="تعداد محصول",
        alias="quantity",
        name="quantity",
        description="quantity",
        dataType="int",
        type="quantity",
        isRequired=False
    )

    @validator("systemCode")
    def system_code_validator(cls, value):
        if not isinstance(value, str):
            raise HTTPException(status_code=400, detail="system_code must be a string")
        if len(value) != 25:
            raise HTTPException(status_code=400, detail="system_code must be 25 characters")
        if ";" in value:
            raise HTTPException(status_code=400, detail="forbidden character ';' in system_code")
        return value

    @validator("quantity")
    def quantity_validator(cls, value):
        if not isinstance(value, int):
            raise HTTPException(status_code=400, detail="quantity must be a int")
        if value > 10000:
            raise HTTPException(status_code=400, detail="quantity must be less than 10000")
        if value < 1:
            raise HTTPException(status_code=400, detail="quantity must be greater than 0")
        return value


class Action(str, Enum):
    add = "add"
    edit = "edit"


class AddToCart(BaseCart):
    basket_id: int = Field(
        title="شناسه سبد",
        alias="basketId",
        name="basketId",
        description="basket Id",
        dataType="int",
        type="Id",
        isRequired=True
    )
    action: Action
    index: Optional[int] = 0
    mandatory_products: List[Product]
    selective_products: List[Product]
    optional_products: Optional[List[Product]]

    # class Config:
    #     schema_extra = {
    #         "example": {
    #             "systemCode": "100101002001",
    #             "storageId": "1",
    #             "count": 1
    #         }
    #     }


class DeleteBasket(BaseModel):
    basket_id: int = Field(
        title="شناسه سبد",
        alias="basketId",
        name="basketId",
        description="basket Id",
        dataType="int",
        type="Id",
        isRequired=True
    )
    index: int
