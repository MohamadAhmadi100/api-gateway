from typing import Optional, List

from fastapi import HTTPException
from pydantic import BaseModel, validator

from source.routers.pricing.validators.customer_validator import CustomerTypeModel


class Price(BaseModel):
    system_code: str
    regular: int
    special: Optional[int] = None
    customer_type: List[CustomerTypeModel] = []

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

    @validator('customer_type')
    def customer_type_validator(cls, value):
        if value:
            if not isinstance(value, list):
                raise HTTPException(status_code=422, detail={"error": "customer_type must be list"})
            elif len(value) >= 255:
                raise HTTPException(status_code=422, detail={"error": "customer_type should be less than 255"})
        return value

    class Config:
        schema_extra = {
            "example": {
                'system_code': "1",
                "regular": 60000000,
                "special": 50000000,
                "customer_type": [
                    {
                        'type': 'B2B',
                        "regular": 60000000,
                        "special": 50000000,
                        "storages": [
                            {
                                "storage_id": "1",
                                "regular": 60000000,
                                "special": 42000000,
                            }
                        ]
                    },
                    {
                        'type': 'B2C',
                        "regular": 60000000,
                        "special": 50000000,
                        "storages": []
                    },
                    {
                        'type': 'B2G',
                        "regular": 60000000,
                        "special": 50000000,
                        "storages": []
                    }]}
        }

    def get(self) -> dict:
        return {
            "system_code": self.system_code,
            'regular': self.regular,
            'special': self.special,
            'customer_type': [type.get() for type in self.customer_type]
        }
