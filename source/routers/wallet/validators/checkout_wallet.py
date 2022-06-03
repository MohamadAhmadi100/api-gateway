from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional


class Type(str, Enum):
    order = "order"


class ChargeType(str, Enum):
    charge_wallet = "charge_wallet"


class ActionType(str, Enum):
    auto = "auto"


class CheckoutBalance(str, Enum):
    consume = "consume"


class ChargeBalance(str, Enum):
    charge = "charge"


class OrderBalance(str, Enum):
    charge = "charge"
    consume = "consume"


class Status(str, Enum):
    success = "success"
    failed = "failed"


class Reserve(BaseModel):
    amount: int = Field(..., alias="amount")
    # wallet_id = int = Field(..., alias="walletId")
    order_number: int = Field(..., alias="orderNumber")
    type: Optional[Type] = Field(..., alias="type")
    action_type: Optional[ActionType] = Field(..., alias="ActionType")
    balance: Optional[CheckoutBalance] = Field(..., alias="balance")


class ResultOrder(BaseModel):
    order_number: int = Field(..., alias="orderNumber")
    # wallet_id = int = Field(..., alias="walletId")
    amount: int = Field(..., alias="amount", isRequired=True)
    type: Optional[Type] = Field(..., alias="type")
    status: Optional[Status] = Field(..., description="success/failed", isRequired=True)
    action_type: Optional[ActionType] = Field(..., alias="ActionType")
    balance: Optional[OrderBalance] = Field(..., alias="balance")


class CompleteOrderWallet(BaseModel):
    order_number: int = Field(..., alias="orderNumber")
    # wallet_id = int = Field(..., alias="walletId")
    amount: int = Field(..., alias="amount", isRequired=True)
    type: Optional[Type] = Field(..., alias="type")
    status: Optional[Status] = Field(..., description="success/failed", isRequired=True)
    action_type: Optional[ActionType] = Field(..., alias="ActionType")
    balance: Optional[CheckoutBalance] = Field(..., alias="balance")
