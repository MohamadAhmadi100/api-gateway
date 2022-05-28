from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel, validator, Field

from source.routers.pricing.validators.customer_validator import CustomerTypeModel


class Price(BaseModel):
    parent_system_code: str = Field(..., alias='parentSystemCode')
    system_code: str = Field(..., alias='systemCode')
    customer_type: CustomerTypeModel = Field({}, alias='customerType')

    @validator("parent_system_code")
    def parent_system_code_validator(cls, value):
        if value is not None:
            if not isinstance(value, str):
                raise HTTPException(status_code=422, detail={"error": "parent_system_code must be str"})
            elif 20 < len(value) or len(value) < 1:
                raise HTTPException(status_code=422,
                                    detail={"error": "parent_system_code must be between 1 and 100000000000000"})
            return value

    @validator("system_code")
    def system_code_validator(cls, value):
        if value is not None:
            if not isinstance(value, str):
                raise HTTPException(status_code=422, detail={"error": "system_code must be str"})
            elif 20 < len(value) or len(value) < 1:
                raise HTTPException(status_code=422,
                                    detail={"error": "system_code must be between 1 and 100000000000000"})
            return value

    class Config:
        schema_extra = {
            "example": {
                "parentSystemCode": "10010100201",
                "systemCode": "100101002001",
                "customerType":
                    {
                        "B2B": {
                            'type': 'B2B',
                            "storages": [
                                {
                                    "storageId": "0",
                                    "regular": 30000000,
                                    'informal': 33000000,
                                    "special": 22000000,
                                    "specialFromDate": "2020-01-01",
                                    "specialToDate": "2020-01-01"
                                },
                                {
                                    "storageId": "1",
                                    "regular": 60000000,
                                    'informal': 33000000,
                                    "special": 42000000,
                                    "specialFromDate": "2020-01-01",
                                    "specialToDate": "2020-01-01"
                                }
                            ]
                        }
                    }
            }
        }

    def get(self) -> dict:
        return {
            'parent_system_code': self.parent_system_code,
            "system_code": self.system_code,
            'customer_type': self.customer_type.dict()
        }


class UpdatePrice(BaseModel):
    system_code: str = Field(..., alias='systemCode')
    customer_type: str = Field(..., alias='customerType')
    storage_id: str = Field(..., alias='storageId')
    regular: int
    informal: Optional[int] = None
    special: Optional[int] = None
    special_from_date: Optional[str] = Field(..., alias='specialFromDate')
    special_to_date: Optional[str] = Field(..., alias='specialToDate')

    @validator("system_code")
    def system_code_validator(cls, value):
        if value is not None:
            if not isinstance(value, str):
                raise HTTPException(status_code=422, detail={"error": "system_code must be str"})
            elif 12 != len(value):
                raise HTTPException(status_code=422,
                                    detail={"error": "system_code must be 12 characters"})
            return value

    @validator("customer_type")
    def customer_type_validator(cls, value):
        if value is not None:
            if not isinstance(value, str):
                raise HTTPException(status_code=422, detail={"error": "customer_type must be str"})
            elif 20 < len(value) or len(value) < 1:
                raise HTTPException(status_code=422,
                                    detail={"error": "customer_type must be between 1 and 20 characters"})
            return value

    @validator("storage_id")
    def storage_id_validator(cls, value):
        if value is not None:
            if not isinstance(value, str):
                raise HTTPException(status_code=422, detail={"error": "storage_id must be str"})
            elif 20 < len(value) or len(value) < 1:
                raise HTTPException(status_code=422,
                                    detail={"error": "storage_id must be between 1 and 20 characters"})
            return value

    @validator("regular")
    def regular_validator(cls, value):
        if value is not None:
            if not isinstance(value, int):
                raise HTTPException(status_code=422, detail={"error": "regular must be int"})
            elif value < 0 or value > 1000000000:
                raise HTTPException(status_code=422, detail={"error": "regular must be between 0 and 1000000000"})
            return value

    @validator("special")
    def special_validator(cls, value):
        if value is not None:
            if not isinstance(value, int):
                raise HTTPException(status_code=422, detail={"error": "special must be int"})
            elif value < 0 or value > 1000000000:
                raise HTTPException(status_code=422, detail={"error": "special must be between 0 and 1000000000"})
            return value

    @validator("special_from_date")
    def special_from_date_validator(cls, value):
        if value is not None:
            if not isinstance(value, str):
                raise HTTPException(status_code=422, detail={"error": "special_from_date must be str"})
            elif 100000000000000 < len(value) or len(value) < 1:
                raise HTTPException(status_code=422,
                                    detail={"error": "special_to_date must be between 1 and 100000000000000"})
            return value

    @validator("special_to_date")
    def special_to_date_validator(cls, value):
        if value is not None:
            if not isinstance(value, str):
                raise HTTPException(status_code=422, detail={"error": "special_to_date must be str"})
            elif 100000000000000 < len(value) or len(value) < 1:
                raise HTTPException(status_code=422,
                                    detail={"error": "special_to_date must be between 1 and 100000000000000"})
            return value

    @validator("informal")
    def informal_validator(cls, value):
        if value is not None:
            if not isinstance(value, int):
                raise HTTPException(status_code=422, detail={"error": "informal must be int"})
            elif value < 0 or value > 1000000000:
                raise HTTPException(status_code=422, detail={"error": "informal must be between 0 and 1000000000"})
            return value

    class Config:
        schema_extra = {
            "example": {
                "systemCode": "100101001001",
                "customerType": "B2B",
                "storageId": "1",
                "regular": 1000000000,
                "special": 50000000,
                "specialFromDate": "2019-01-01 00:00:00",
                "specialToDate": "2019-01-01 00:00:00"
            }
        }
