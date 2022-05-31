from fastapi import HTTPException
from pydantic import validator, BaseModel, Field

from source.routers.quantity.validators.customer_type import CustomerTypeModel


class Quantity(BaseModel):
    parent_system_code: str = Field(..., alias="parentSystemCode")
    system_code: str = Field(..., alias="systemCode")
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

    class Config:
        schema_extra = {
            "example": {
                "parentSystemCode": "10010100201",
                "systemCode": "100101002001",
                "customerTypes": {
                    "B2B": {
                        "type": 'B2B',
                        "storages": [
                            {
                                "storageId": "0",
                                "stockForSale": 200,
                                "minQty": 1,
                                "maxQty": 100,
                            },
                            {
                                "storageId": "1",
                                "stockForSale": 50,
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
            "parent_system_code": self.parent_system_code,
            "system_code": self.system_code,
            "customer_types": self.customer_types.dict()
        }


class UpdateQuantity(BaseModel):
    system_code: str = Field(..., alias="systemCode")
    customer_type: str = Field(..., alias="customerType")
    storage_id: str = Field(..., alias="storageId")
    stock_for_sale: int = Field(None, alias="stockForSale")
    min_qty: int = Field(None, alias="minQty")
    max_qty: int = Field(None, alias="maxQty")

    @validator("system_code")
    def system_code_validator(cls, value):
        if not isinstance(value, str):
            raise HTTPException(status_code=422, detail={"error": "system_code must be str"})
        elif len(value) != 12:
            raise HTTPException(status_code=422, detail={"error": "system_code must be 12 length"})
        return value

    @validator("customer_type")
    def customer_type_validator(cls, value):
        if not isinstance(value, str):
            raise HTTPException(status_code=422, detail={"error": "customer_type must be str"})
        elif value not in ["B2B", "B2C", "B2G"]:
            raise HTTPException(status_code=422, detail={"error": "customer_type must be B2B, B2C, B2G"})
        return value

    @validator("storage_id")
    def storage_id_validator(cls, value):
        if not isinstance(value, str):
            raise HTTPException(status_code=422, detail={"error": "storage_id must be str"})
        elif int(value) > 10000:
            raise HTTPException(status_code=422, detail={"error": "storage_id must be less than 10000"})
        return value

    @validator("stock_for_sale")
    def stock_for_sale_validator(cls, value):
        if not isinstance(value, int):
            raise HTTPException(status_code=422, detail={"error": "stock_for_sale must be int"})
        elif value < 0 or value > 100000000000:
            raise HTTPException(status_code=422, detail={"error": "stock_for_sale must be between 0 and 100000000000"})
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
                "systemCode": "123456789012",
                "customerType": "B2B",
                "storageId": "1",
                "stockForSale": 100,
                "minQty": 1,
                "maxQty": 100
            }
        }
