
from pydantic import BaseModel, Field
from typing import Dict, Optional, Union


class Insurance(BaseModel):
    insuranceType: str
    typeLabel: str
    amount: int
    coverage: str


class PerStock(BaseModel):
    stockId: str = Field()
    shippingMethod: str = Field(isRequired=True)
    shippingAddress: str
    shippingCity: str
    shippingCityId: str
    shippingState: str
    shippingStateId: str
    shippingMobile: Optional[str]
    receiverName: Optional[str]
    receiverNationalId: Optional[str]
    insurance: Union[Insurance]
