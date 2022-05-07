from fastapi import HTTPException
from pydantic import BaseModel, validator, Field


class BaseCart(BaseModel):
    pass


class check_out(BaseCart):
    type: str = Field(..., alias="actionType")
    data: dict = Field(..., alias="requiredData")

