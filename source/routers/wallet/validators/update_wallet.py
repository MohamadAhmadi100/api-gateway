from enum import Enum
import re
from typing import Optional
from fastapi import HTTPException
from pydantic import BaseModel, Field, validator


class Balance(str, Enum):
    charge = "charge"
    consume = "consume"


class Type(str, Enum):
    staff_charge = "staffCharge"
    staff_consume = "staffConsume"


class ActionType(str, Enum):
    manual = "manual"


class UpdateData(BaseModel):
    staff_name: str = Field(..., alias="staffName")
    staff_id: int = Field(..., alias="staffId")
    amount: int = Field(..., alias="amount", isRequired=True)
    balance: Optional[Balance] = Field(..., description="charge/consume", isRequired=True)
    action_type: Optional[ActionType] = Field(..., alias="ActionType")
    type: Optional[Type] = Field(..., alias="type")
    description: str = Field(min_length=5, max_length=300, isRequired=False)
    reason: str = Field(min_length=5, max_length=50, isRequired=True)

    @validator("description")
    def validate_description(cls, description):
        pattern = r"^[\u0600-\u06FF ]{5,300}$"
        match = re.findall(pattern, description)
        if not match:
            raise HTTPException(status_code=422, detail={"error": "توضیحات صحیح نیست"})
        return description

    @validator("reason")
    def validate_reason(cls, reason):
        pattern = r"^[\u0600-\u06FF ]{5,50}$"
        match = re.findall(pattern, reason)
        if not match:
            raise HTTPException(status_code=422, detail={"error": "توضیحات صحیح نیست"})
        return reason
