from pydantic import BaseModel, Field
from typing import List, Union, Optional



class IMEI(BaseModel):
    product: dict = Field(alias="product")
    customer_id: str = Field(alias="customerId")
    referral_number: str = Field(alias="referralNumber")