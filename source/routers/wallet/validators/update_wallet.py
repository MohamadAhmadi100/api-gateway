from datetime import datetime
from enum import Enum
import re

from fastapi import HTTPException
from pydantic import BaseModel, Field, validator


class UpdateData(BaseModel):
    user_name: str = Field(..., alias="userName")
    user_id: int = Field(..., alias="userId")
    customer_id: int = Field(..., alias="customerId", isRequired=True)
    amount_of_money: int = Field(..., alias="amountOfMoney", isRequired=True)
    type: bool = Field(..., isRequired=True)
    description: str = Field(min_length=5, max_length=300, isRequired=True)

    @validator("description")
    def validate_street(cls, description):
        pattern = r"^[\u0600-\u06FF ]{5,300}$"
        match = re.findall(pattern, description)
        if not match:
            raise HTTPException(status_code=422, detail={"error": "توضیحات صحیح نیست"})
        return description
