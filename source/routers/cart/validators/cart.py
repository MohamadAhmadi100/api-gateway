from fastapi import HTTPException
from pydantic import BaseModel, validator, Field


class BaseCart(BaseModel):
    pass


class Cart(BaseCart):
    user_info: dict = Field(..., alias="userInfo")
    # status: str = "in_cart"


class AddCart(BaseCart):
    system_code: str = Field(..., alias="systemCode")
    storage_id: str = Field(..., alias="storageId")
    count: int

    @validator("system_code")
    def system_code_validator(cls, value):
        if not isinstance(value, str):
            raise HTTPException(status_code=400, detail="system_code must be a string")
        if len(value) != 25:
            raise HTTPException(status_code=400, detail="system_code must be 25 characters")
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
        if value > 10000:
            raise HTTPException(status_code=400, detail="count must be less than 10000")
        return value

    class Config:
        schema_extra = {
            "example": {
                "systemCode": "100101002001",
                "storageId": "1",
                "count": 1
            }
        }

class AddCreditCart(AddCart):
    days: int = Field(..., alias="days")

    @validator("days")
    def days_validator(cls, value):
        if not isinstance(int(value), int):
            raise HTTPException(status_code=400, detail="days must be a int")
        if value < 0:
            raise HTTPException(status_code=400, detail="days must be greater than 0")
        return int(value)

    class Config:
        schema_extra = {
            "example": {
                "systemCode": "100101002001",
                "storageId": "1",
                "count": 1,
                "days": 1
            }
        }