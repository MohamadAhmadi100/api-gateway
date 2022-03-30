from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel, validator, Field

from source.routers.pricing.validators.customer_validator import CustomerTypeModel


class Price(BaseModel):
    parent_system_code: str = Field(..., alias='parentSystemCode')
    system_code: str = Field(..., alias='systemCode')
    regular: int
    special: Optional[int] = None
    special_from_date: str = Field(..., alias='specialFromDate')
    special_to_date: str = Field(..., alias='specialToDate')
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

    @validator("regular")
    def regular_validator(cls, value):
        if not isinstance(value, int):
            raise HTTPException(status_code=422, detail={"error": "regular must be int"})
        elif 100000000000000 < value or value < 1:
            raise HTTPException(status_code=422, detail={"error": "regular must be between 1 and 100000000000000"})
        return value

    @validator("special")
    def special_validator(cls, value):
        if value:
            if not isinstance(value, int):
                raise HTTPException(status_code=422, detail={"error": "special must be int"})
            elif 100000000000000 < value or value < 1:
                raise HTTPException(status_code=422, detail={"error": "special must be between 1 and 100000000000000"})
        return value

    @validator("special_from_date")
    def special_from_date_validator(cls, value):
        if not isinstance(value, str):
            raise HTTPException(status_code=422, detail={"error": "special_from_date must be str"})
        elif 100000000000000 < len(value) or len(value) < 1:
            raise HTTPException(status_code=422,
                                detail={"error": "special_from_date must be between 1 and 100000000000000"})
        return value

    @validator("special_to_date")
    def special_to_date_validator(cls, value):
        if not isinstance(value, str):
            raise HTTPException(status_code=422, detail={"error": "special_to_date must be str"})
        elif 100000000000000 < len(value) or len(value) < 1:
            raise HTTPException(status_code=422,
                                detail={"error": "special_to_date must be between 1 and 100000000000000"})
        return value

    class Config:
        schema_extra = {
            "example": {
                "parentSystemCode": "10010100201",
                "systemCode": "100101002001",
                "regular": 60000000,
                "special": 50000000,
                "specialFromDate": "2020-01-01",
                "specialToDate": "2020-01-01",
                "customerType":
                    {
                        "B2B": {
                            'type': 'B2B',
                            "regular": 60000000,
                            "special": 50000000,
                            "specialFromDate": "2020-01-01",
                            "specialToDate": "2020-01-01",
                            "storages": [
                                {
                                    "storageId": "0",
                                    "regular": 30000000,
                                    "special": 22000000,
                                    "specialFromDate": "2020-01-01",
                                    "specialToDate": "2020-01-01"
                                },
                                {
                                    "storageId": "1",
                                    "regular": 60000000,
                                    "special": 42000000,
                                    "specialFromDate": "2020-01-01",
                                    "specialToDate": "2020-01-01"
                                }
                            ]
                        },
                        "B2C": {
                            'type': 'B2C',
                            "regular": 60000000,
                            "special": 50000000,
                            "specialFromDate": "2020-01-01",
                            "specialToDate": "2020-01-01",
                            "storages": []
                        },
                        "B2G": {
                            'type': 'B2G',
                            "regular": 60000000,
                            "special": 50000000,
                            "specialFromDate": "2020-01-01",
                            "specialToDate": "2020-01-01",
                            "storages": []
                        }
                    }
            }
        }

    def get(self) -> dict:
        return {
            'parent_system_code': self.parent_system_code,
            "system_code": self.system_code,
            'regular': self.regular,
            'special': self.special,
            'special_from_date': self.special_from_date,
            'special_to_date': self.special_to_date,
            'customer_type': self.customer_type.dict()
        }
