from fastapi import HTTPException
from pydantic import BaseModel, validator


class BaseCart(BaseModel):
    pass


class Cart(BaseCart):
    user_info: dict
    # status: str = "in_cart"


class AddCart(BaseCart):
    system_code: str
    storage_id: str
    count: int

    @validator("system_code")
    def system_code_validator(cls, value):
        if not isinstance(value, str):
            raise HTTPException(status_code=400, detail="system_code must be a string")
        if len(value) != 9:
            raise HTTPException(status_code=400, detail="system_code must be 9 characters")
        if ";" in value:
            raise HTTPException(status_code=400, detail="forbidden character ';' in system_code")
        return value

    @validator("storage_id")
    def storage_id_validator(cls, value):
        if not isinstance(value, str):
            raise HTTPException(status_code=400, detail="storage_id must be a string")
        if len(value) < 1 or len(value) > 10:
            raise HTTPException(status_code=400, detail="storage_id must be between 1 and 10 characters")
        return value

    @validator("count")
    def count_validator(cls, value):
        if not isinstance(value, int):
            raise HTTPException(status_code=400, detail="count must be a string")
        if value < 1 or value > 10000:
            raise HTTPException(status_code=400, detail="count must be between 1 and 10000")
        return value

    class Config:
        schema_extra = {
            "example": {
                "system_code": "100101001001",
                "storage_id": "1",
                "count": 1
            }
        }
