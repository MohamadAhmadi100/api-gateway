from typing import List, Optional

from fastapi import HTTPException
from pydantic import BaseModel, validator, Field

from source.routers.quantity.validators.storage import Storage


class CustomerType(BaseModel):
    type: str
    stock_for_sale: int = Field(..., alias='stockForSale')
    reserved = 0
    storages: List[Storage]

    @validator("type")
    def type_validator(cls, value):
        if not isinstance(value, str):
            raise HTTPException(status_code=422, detail={"error": "type must be str"})
        elif 127 < len(value) or len(value) < 1:
            raise HTTPException(status_code=422, detail={"error": "type must be between 1 and 127"})
        return value

    @validator("stock_for_sale")
    def stock_for_sale_validator(cls, value):
        if not isinstance(value, int):
            raise HTTPException(status_code=422, detail={"error": "stock_for_sale must be int"})
        elif 100_000_000_000_000 < value or value < 1:
            raise HTTPException(status_code=422,
                                detail={"error": "stock_for_sale must be between 1 and 100_000_000_000_000"})
        return value

    @validator("storages")
    def storages_validator(cls, value):
        if not isinstance(value, list):
            raise HTTPException(status_code=422, detail={"error": "storages must be list"})
        elif 127 < len(value) or len(value) < 1:
            raise HTTPException(status_code=422, detail={"error": "storages must be between 1 and 127"})
        return value

    def get(self):
        return {
            "type": self.type,
            "stock_for_sale": self.stock_for_sale,
            "storages": [storage.get() for storage in self.storages]
        }


class CustomerTypeModel(BaseModel):
    B2B: Optional[CustomerType] = {}
    B2C: Optional[CustomerType] = {}
    B2G: Optional[CustomerType] = {}
