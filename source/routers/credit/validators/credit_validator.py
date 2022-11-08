from fastapi import HTTPException, Query
from pydantic import BaseModel, Field, validator
from typing import Optional, Union

class AddCredit(BaseModel):
    amount: int = Field(..., alias="amount")
    payment_type: str = Field(..., alias="paymentType")
    description: str = Field(...)

    @validator('payment_type')
    def validate_payment_type(cls, payment_type):
        if payment_type not in ['cheque', 'online_payment']:
            raise HTTPException(status_code=422, detail={"error": "نوع متد پرداخت معتبر نیست"})
        return payment_type

class AcceptCredit(BaseModel):
    referral_number: str = Field(..., alias="referralNumber")



class RequestsDetail(BaseModel):
    referral_number: Optional[str] = Field(..., alias="referralNumber")
    date_from: Optional[str] = Field(..., alias="dateFrom")
    date_to: Optional[str] = Field(..., alias="dateTo")
    page: int = Field(..., alias="page")
    per_page: int = Field(..., alias="perPage")
    accepted: Optional[bool] = Field(..., alias="accepted")
    search_box: Optional[str] = Field(..., alias="searchBox")



class AccountingRecords(BaseModel):
    dealership_name: Optional[str] = Field(..., alias="dealershipName")
    order_number: Optional[str] = Field(..., alias="orderNumber")
    date_from: Optional[str] = Field(..., alias="dateFrom")
    date_to: Optional[str] = Field(..., alias="dateTo")
    page: Union[int, None] = Query(default=1, alias="page")
    per_page: Union[int, None] = Query(default=15, alias="perPage")
    payment_status: Optional[bool] = Field(..., alias="paymentStatus")
    unit_price_to: Optional[str] = Field(..., alias="unitPriceTo")
    unit_price_from: Optional[str] = Field(..., alias="unitPriceFrom")
    total_price_from: Optional[str] = Field(..., alias="totalPriceFrom")
    total_price_to: Optional[str] = Field(..., alias="totalPriceTo")
    count_from: Optional[str] = Field(..., alias="countFrom")
    count_to: Optional[str] = Field(..., alias="countTo")
    wage_from: Optional[str] = Field(..., alias="wageFrom")
    wage_to: Optional[str] = Field(..., alias="wageTo")
