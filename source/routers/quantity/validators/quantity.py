from typing import List

from fastapi import HTTPException
from pydantic import validator, BaseModel

from source.routers.quantity.validators.customer_type import CustomerType


class Quantity(BaseModel):
    parent_system_code: str
    system_code: str
    stock: int
    total_stock_for_sale: int
    customer_types: CustomerType = {}

    @validator("parent_system_code")
    def parent_system_code_validator(cls, value):
        if not isinstance(value, str):
            raise HTTPException(status_code=422, detail={"error": "parent_system_code must be str"})
        elif 127 < len(value) or len(value) < 1:
            raise HTTPException(status_code=422, detail={"error": "parent_system_code must be between 1 and 127"})
        return value

    @validator("system_code")
    def system_code_validator(cls, value):
        if not isinstance(value, str):
            raise HTTPException(status_code=422, detail={"error": "system_code must be str"})
        elif 127 < len(value) or len(value) < 1:
            raise HTTPException(status_code=422, detail={"error": "system_code must be between 1 and 127"})
        return value

    @validator("stock")
    def stock_validator(cls, value):
        if not isinstance(value, int):
            raise HTTPException(status_code=422, detail={"error": "stock must be int"})
        elif 100_000_000_000_000 < value or value < 1:
            raise HTTPException(status_code=422,
                                detail={"error": "stock must be between 1 and 100_000_000_000_000"})
        return value

    @validator("total_stock_for_sale")
    def total_stock_for_sale_validator(cls, value):
        if not isinstance(value, int):
            raise HTTPException(status_code=422, detail={"error": "total_stock_for_sale must be int"})
        elif 100_000_000_000_000 < value or value < 1:
            raise HTTPException(status_code=422,
                                detail={"error": "total_stock_for_sale must be between 1 and 100_000_000_000_000"})
        return value

    @validator("customer_types")
    def customer_types_validator(cls, value):
        if not isinstance(value, list):
            raise HTTPException(status_code=422, detail={"error": "customer_types must be array"})
        elif 127 < len(value) or len(value) < 1:
            raise HTTPException(status_code=422, detail={"error": "customer_types must be between 1 and 127"})
        return value

    class Config:
        schema_extra = {
            "example": {
                "parent_system_code": "1",
                "system_code": '1000',
                "stock": 1,
                "total_stock_for_sale": 1,
                "customer_types": [
                    {
                        "type": 'B2B',
                        "stock_for_sale": 1
                    }
                ],
                "storages": [
                    {
                        "storage_id": "0",
                        "stock": 1,
                        "stock_for_sale": 1,
                    },
                    {
                        "storage_id": "0",
                        "stock": 1,
                        "stock_for_sale": 1,
                    }
                ]
            }
        }

    def get(self):
        return {
            "parent_system_code": self.parent_system_code,
            "system_code": self.system_code,
            "stock": self.stock,
            "total_stock_for_sale": self.total_stock_for_sale,
            "customer_types": [type.get() for type in self.customer_types],
        }
