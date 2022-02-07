from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel, validator

from source.routers.pricing.validators.customer_validator import CustomerTypeModel


class Price(BaseModel):
    parent_system_code: str
    system_code: str
    regular: int
    special: Optional[int] = None
    customer_type: CustomerTypeModel = {}

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

    class Config:
        schema_extra = {
            "example": {
                "parent_system_code": "10010100201",
                "system_code": "100101002001",
                "regular": 60000000,
                "special": 50000000,
                "customer_type":
                    {
                        "B2B": {
                            'type': 'B2B',
                            "regular": 60000000,
                            "special": 50000000,
                            "storages": [
                                {
                                    "storage_id": "0",
                                    "regular": 30000000,
                                    "special": 22000000,
                                },
                                {
                                    "storage_id": "1",
                                    "regular": 60000000,
                                    "special": 42000000,
                                }
                            ]
                        },
                        "B2C": {
                            'type': 'B2C',
                            "regular": 60000000,
                            "special": 50000000,
                            "storages": []
                        },
                        "B2G": {
                            'type': 'B2G',
                            "regular": 60000000,
                            "special": 50000000,
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
            'customer_type': self.customer_type.dict()
        }
