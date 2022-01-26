from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel, validator


class AddCart(BaseModel):
    user_id: int
    system_code: str
    status: Optional[str] = "in_cart"
    storage_id: str
    count: int

    @validator("user_id")
    def user_id_validator(self, value):
        if not isinstance(value, int):
            raise HTTPException(status_code=400, detail="user_id must be a string")
        if value < 1 or value > 100:
            raise HTTPException(status_code=400, detail="user_id must be between 1 and 100")
        return value

    @validator("system_code")
    def system_code_validator(self, value):
        if not isinstance(value, str):
            raise HTTPException(status_code=400, detail="system_code must be a string")
        if len(value) != 12:
            raise HTTPException(status_code=400, detail="system_code must be 12 characters")
        return value

    @validator("status")
    def status_validator(self, value):
        if not isinstance(value, str):
            raise HTTPException(status_code=400, detail="status must be a string")
        if value not in ["in_cart"]:
            raise HTTPException(status_code=400, detail="status must be in_cart or in_storage")
        return value

    @validator("storage_id")
    def storage_id_validator(self, value):
        if not isinstance(value, str):
            raise HTTPException(status_code=400, detail="storage_id must be a string")
        if len(value) < 1 or len(value) > 10:
            raise HTTPException(status_code=400, detail="storage_id must be between 1 and 10 characters")
        return value

    @validator("count")
    def count_validator(self, value):
        if not isinstance(value, int):
            raise HTTPException(status_code=400, detail="count must be a string")
        if value < 1 or value > 10000:
            raise HTTPException(status_code=400, detail="count must be between 1 and 10000")
        return value
