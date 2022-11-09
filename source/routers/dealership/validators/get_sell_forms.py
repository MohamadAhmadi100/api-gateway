from pydantic import BaseModel, Field
from typing import List, Union, Optional, Dict

class SellForms(BaseModel):
    dealership_id: Optional[int] = Field(alias="dealershipId")
    customer_id: Optional[int] = Field(alias="dealershipId")
    page: Union[int, None] = Field(default=1),
    per_page: Union[int, None] = Field(default=1, alias="perPage"),
    order_number: Optional[int] = Field(alias="orderNumber")
    payment_status: Optional[bool] = Field(alias="paymentStatus")
    customer_name: Optional[str] = Field(alias="customerName")
    date_from: Optional[str] = Field(alias="dateFrom")
    date_to: Optional[str] = Field(alias="dateTo")
    status: Optional[str]
