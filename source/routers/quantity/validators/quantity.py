from fastapi import HTTPException
from pydantic import validator, BaseModel, Field

from source.routers.quantity.validators.customer_type import CustomerTypeModel


class Quantity(BaseModel):
    parent_system_code: str = Field(..., alias="parentSystemCode")
    system_code: str = Field(..., alias="systemCode")
    stock: int
    reserved = 0
    total_stock_for_sale: int = Field(..., alias="totalStockForSale")
    customer_types: CustomerTypeModel = Field({}, alias="customerTypes")

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

    class Config:
        schema_extra = {
            "example": {
                "parentSystemCode": "10010100201",
                "systemCode": "100101002001",
                "stock": 500,
                "totalStockForSale": 250,
                "customerTypes": {
                    "B2B": {
                        "type": 'B2B',
                        "stockForSale": 250,
                        "storages": [
                            {
                                "storageId": "0",
                                "stock": 400,
                                "stockForSale": 200,
                                "minQty": 1,
                                "maxQty": 100,
                                "orderLimit": 5
                            },
                            {
                                "storageId": "1",
                                "stock": 100,
                                "stockForSale": 50,
                                "minQty": 1,
                                "maxQty": 100,
                                "orderLimit": 5
                            }
                        ]
                    }
                }

            }
        }

    def get(self):
        return {
            "parent_system_code": self.parent_system_code,
            "system_code": self.system_code,
            "stock": self.stock,
            "reserved": self.reserved,
            "total_stock_for_sale": self.total_stock_for_sale,
            "customer_types": self.customer_types.dict()
        }
