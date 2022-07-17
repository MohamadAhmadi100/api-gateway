from fastapi import HTTPException
from pydantic import BaseModel, validator, Field


class add_credit(BaseModel):
    amount: int = Field(..., alias="amount")
    payment_type: str = Field(..., alias="paymentType")


class accept_credit(BaseModel):
    referral_number: int = Field(..., alias="referral_number")
