from typing import List, Optional

from fastapi import HTTPException
from pydantic import BaseModel, validator, Field


class Storage(BaseModel):
    storage_id: str = Field(..., alias="storageId")
    reserved = 0
    quantity: int = Field(..., alias="quantity")
    min_qty: int = Field(..., alias="minQty")
    max_qty: int = Field(..., alias="maxQty")

    @validator("storage_id")
    def storage_id_validator(cls, value):
        if not isinstance(value, str):
            raise HTTPException(status_code=422, detail={"error": "storage_id must be str"})
        elif 127 < len(value) or len(value) < 1:
            raise HTTPException(status_code=422, detail={"error": "storage_id must be between 1 and 127"})
        return value

    @validator("quantity")
    def stock_for_sale_validator(cls, value):
        if not isinstance(value, int):
            raise HTTPException(status_code=422, detail={"error": "quantity must be int"})
        elif 100_000_000_000_000 < value or value < 0:
            raise HTTPException(status_code=422,
                                detail={"error": "quantity must be between 0 and 100_000_000_000_000"})
        return value

    @validator("min_qty")
    def min_qty_validator(cls, value):
        if not isinstance(value, int):
            raise HTTPException(status_code=422, detail={"error": "min_qty must be int"})
        elif 100_000_000_000_000 < value or value < 1:
            raise HTTPException(status_code=422,
                                detail={"error": "min_qty must be between 1 and 100_000_000_000_000"})
        return value

    @validator("max_qty")
    def max_qty_validator(cls, value):
        if not isinstance(value, int):
            raise HTTPException(status_code=422, detail={"error": "max_qty must be int"})
        elif 100_000_000_000_000 < value or value < 1:
            raise HTTPException(status_code=422,
                                detail={"error": "max_qty must be between 1 and 100_000_000_000_000"})
        return value

    def get(self):
        return {
            "storage_id": self.storage_id,
            "quantity": self.quantity
        }


class CustomerType(BaseModel):
    type: str
    storages: List[Storage]

    @validator("type")
    def type_validator(cls, value):
        if not isinstance(value, str):
            raise HTTPException(status_code=422, detail={"error": "type must be str"})
        elif 127 < len(value) or len(value) < 1:
            raise HTTPException(status_code=422, detail={"error": "type must be between 1 and 127"})
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
            "storages": [storage.get() for storage in self.storages]
        }


class CustomerTypeModel(BaseModel):
    B2B: Optional[CustomerType] = {
        "type": "B2B",
    }
    B2C: Optional[CustomerType] = {
        "type": "B2C",
    }
    B2G: Optional[CustomerType] = {
        "type": "B2G"
    }


class Quantity(BaseModel):
    system_code: str = Field(..., alias="systemCode")
    customer_types: CustomerTypeModel = Field({}, alias="customerTypes")

    @validator("system_code")
    def system_code_validator(cls, value):
        if not isinstance(value, str):
            raise HTTPException(status_code=422, detail={"error": "system_code must be str"})
        elif 127 < len(value) or len(value) < 1:
            raise HTTPException(status_code=422, detail={"error": "system_code must be between 1 and 127"})
        return value

    class Config:
        schema_extra = {
            "example": {
                "systemCode": "100101002001",
                "customerTypes": {
                    "B2B": {
                        "type": 'B2B',
                        "storages": [
                            {
                                "storageId": "0",
                                "quantity": 200,
                                "minQty": 1,
                                "maxQty": 100,
                            },
                            {
                                "storageId": "1",
                                "quantity": 50,
                                "minQty": 1,
                                "maxQty": 100,
                            }
                        ]
                    }
                }

            }
        }

    def get(self):
        return {
            "system_code": self.system_code,
            "customer_types": self.customer_types.dict()
        }


class UpdateQuantity(BaseModel):
    system_code: str = Field(..., alias="systemCode")
    customer_type: str = Field(..., alias="customerType")
    storage_id: str = Field(..., alias="storageId")
    quantity: int = Field(None, alias="quantity")
    min_qty: int = Field(None, alias="minQty")
    max_qty: int = Field(None, alias="maxQty")

    @validator("system_code")
    def system_code_validator(cls, value):
        if not isinstance(value, str):
            raise HTTPException(status_code=422, detail={"error": "system_code must be str"})
        elif len(value) != 25:
            raise HTTPException(status_code=422, detail={"error": "system_code must be 25 length"})
        return value

    @validator("customer_types")
    def customer_type_validator(cls, value):
        if not isinstance(value, str):
            raise HTTPException(status_code=422, detail={"error": "customer_types must be str"})
        elif value not in ["B2B", "B2C", "B2G"]:
            raise HTTPException(status_code=422, detail={"error": "customer_types must be B2B, B2C, B2G"})
        return value

    @validator("storage_id")
    def storage_id_validator(cls, value):
        if not isinstance(value, str):
            raise HTTPException(status_code=422, detail={"error": "storage_id must be str"})
        elif int(value) > 10000:
            raise HTTPException(status_code=422, detail={"error": "storage_id must be less than 10000"})
        return value

    @validator("quantity")
    def stock_for_sale_validator(cls, value):
        if not isinstance(value, int):
            raise HTTPException(status_code=422, detail={"error": "quantity must be int"})
        elif value < 0 or value > 100000000000:
            raise HTTPException(status_code=422, detail={"error": "quantity must be between 0 and 100000000000"})
        return value

    @validator("min_qty")
    def min_qty_validator(cls, value):
        if not isinstance(value, int):
            raise HTTPException(status_code=422, detail={"error": "min_qty must be int"})
        elif value < 0 or value > 100000000000:
            raise HTTPException(status_code=422, detail={"error": "min_qty must be between 0 and 100000000000"})
        return value

    @validator("max_qty")
    def max_qty_validator(cls, value):
        if not isinstance(value, int):
            raise HTTPException(status_code=422, detail={"error": "max_qty must be int"})
        elif value < 0 or value > 100000000000:
            raise HTTPException(status_code=422, detail={"error": "max_qty must be between 0 and 100000000000"})
        return value

    class Config:
        schema_extra = {
            "example": {
                "systemCode": "2000010010001001001001001",
                "customerType": "B2B",
                "storageId": "1",
                "quantity": 100,
                "minQty": 1,
                "maxQty": 100
            }
        }
