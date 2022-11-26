from pydantic import BaseModel, Field
from typing import Union, Optional

class GetRequestGood(BaseModel):
    page: Union[int, None] = Field(default=1)
    per_page: Union[int, None] = Field(default=15, alias="perPage")
    referral_number: Optional[int] = Field(alias="referralNumber")
    date_from: Optional[str] = Field(alias="dateFrom")
    date_to: Optional[str] = Field(alias="dateTo")
    status: Optional[str]
