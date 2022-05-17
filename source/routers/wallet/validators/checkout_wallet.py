from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional


class Type(str, Enum):
    order = "order"
class CancelType(str, Enum):
    cancel_order = "cancel_order"


class ActionType(str, Enum):
    auto = "auto"


class CheckoutBalance(str, Enum):
    consume = "consume"


class OrderBalance(str, Enum):
    charge = "charge"
    consume = "consume"


class Status(str, Enum):
    success = "success"
    failed = "failed"


class Reserve(BaseModel):
    amount: int = Field(..., alias="amount")
    order_number: int = Field(..., alias="orderNumber")
    type: Optional[Type] = Field(..., alias="type")
    action_type: Optional[ActionType] = Field(..., alias="ActionType")
    balance: Optional[CheckoutBalance] = Field(..., alias="balance")


class Order(BaseModel):
    order_number: int = Field(..., alias="orderNumber")
    amount: int = Field(..., alias="amount", isRequired=True)
    type: Optional[Type] = Field(..., alias="type")
    status: Optional[Status] = Field(..., description="success/failed", isRequired=True)
    action_type: Optional[ActionType] = Field(..., alias="ActionType")
    balance: Optional[OrderBalance] = Field(..., alias="balance")


class OrderWallet(BaseModel):
    order_number: int = Field(..., alias="orderNumber")
    amount: int = Field(..., alias="amount", isRequired=True)
    type: Optional[Type] = Field(..., alias="type")
    status: Optional[Status] = Field(..., description="success/failed", isRequired=True)
    action_type: Optional[ActionType] = Field(..., alias="ActionType")
    balance: Optional[CheckoutBalance] = Field(..., alias="balance")


class CancelOrder(BaseModel):
    order_number: int = Field(..., alias="orderNumber")
    amount: int = Field(..., alias="amount", isRequired=True)
    type: Optional[CancelType] = Field(..., alias="type")
