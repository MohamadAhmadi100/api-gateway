from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional


class Type(str, Enum):
    order = "order"


class ActionType(str, Enum):
    auto = "auto"


class Balance(str, Enum):
    balance = "consume"


class Reserve(BaseModel):
    amount: int = Field(..., alias="amount")
    order_number: int = Field(..., alias="orderNumber")
    type: Optional[Type] = Field(..., alias="type")
    Action_type: Optional[ActionType] = Field(..., alias="ActionType")
    balance: Optional[Balance] = Field(..., alias="balance")
