
from pydantic import BaseModel, Field
from typing import Dict, Optional, Union


class Insurance(BaseModel):
    insuranceType: str
    typeLabel: str
    amount: int
    coverage: str
    selectedType: str


class PerStock(BaseModel):
    stockId: str = Field()
    totalPrice : Optional[int] = Field(isRequired=False)
    totalItem: int
    shippingMethod: str = Field(isRequired=True)
    shippingAddress: str
    shippingCity: str
    shippingCityId: str
    shippingState: str
    shippingStateId: str
    shippingMobile: Optional[str]
    receiverFirstName: Optional[str]
    receiverLastName: Optional[str]
    receiverNationalId: Optional[str]
    receiverPhoneNumber: Optional[str]
    insurance: Union[Insurance]
