from fastapi import HTTPException
from pydantic import BaseModel, validator, Field


class Storage(BaseModel):
    storage_id: str = Field(..., alias="storageId")
    reserved = 0
    stock_for_sale: int = Field(..., alias="stockForSale")
    min_qty: int = Field(..., alias="minQty")
    max_qty: int = Field(..., alias="maxQty")

    @validator("storage_id")
    def storage_id_validator(cls, value):
        if not isinstance(value, str):
            raise HTTPException(status_code=422, detail={"error": "storage_id must be str"})
        elif 127 < len(value) or len(value) < 1:
            raise HTTPException(status_code=422, detail={"error": "storage_id must be between 1 and 127"})
        return value

    @validator("stock_for_sale")
    def stock_for_sale_validator(cls, value):
        if not isinstance(value, int):
            raise HTTPException(status_code=422, detail={"error": "stock_for_sale must be int"})
        elif 100_000_000_000_000 < value or value < 1:
            raise HTTPException(status_code=422,
                                detail={"error": "stock_for_sale must be between 1 and 100_000_000_000_000"})
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
            "stock": self.stock,
            "stock_for_sale": self.stock_for_sale
        }
