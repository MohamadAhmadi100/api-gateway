from enum import Enum
import re
from typing import Optional
from fastapi import HTTPException,Query
from pydantic import BaseModel, Field, validator


class Balance(str, Enum):
    charge = "charge"
    consume = "consume"


class Type(str, Enum):
    staff_charge = "staffCharge"
    staff_consume = "staffConsume"
    customer_charge = "customerCharge"


class ActionType(str, Enum):
    manual = "manual"
    auto = "auto"


class UpdateData(BaseModel):
    staff_name: str = Field(..., alias="staffName")
    customer_id : int = Field(..., alias="customerId")
    amount: int = Field(..., alias="amount", isRequired=True)
    balance: Optional[Balance] = Field(..., description="charge/consume", isRequired=True)
    action_type: Optional[ActionType] = Field(..., alias="ActionType")
    type: Optional[Type] = Field(..., alias="type")
    description: str = Query(None)
    reason: dict = Field(alias="reason", isRequired=True)

