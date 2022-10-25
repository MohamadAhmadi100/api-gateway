from fastapi import HTTPException
from pydantic import BaseModel, Field, validator
from typing import Optional

class AddCredit(BaseModel):
    amount: int = Field(..., alias="amount")
    payment_type: str = Field(..., alias="paymentType")

    @validator('payment_type')
    def validate_payment_type(cls, payment_type):
        if payment_type not in ['cheque', 'online_payment']:
            raise HTTPException(status_code=422, detail={"error": "نوع متد پرداخت معتبر نیست"})
        return payment_type

class AcceptCredit(BaseModel):
    referral_number: str = Field(..., alias="referralNumber")



class RequestsDetail(BaseModel):
    referral_number: Optional[str] = Field(..., alias="referralNumber")
    date_from: Optional[str]  = Field(..., alias="dateFrom")
    date_to: Optional[str]  = Field(..., alias="dateTo")
    page: int = Field(..., alias="page")
    per_page: int = Field(..., alias="perPage")
    accepted: Optional[bool]  = Field(..., alias="accepted")
    search_box: Optional[str]  = Field(..., alias="searchBox")
