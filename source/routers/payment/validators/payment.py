from enum import Enum
from fastapi import HTTPException
from pydantic import BaseModel, validator, Field
from typing import Optional

class CustomerType(str, Enum):
    B2B = "B2B"
    B2C = "B2C"

class Services(str, Enum):
    wallet= "wallet"
    order = "order"
    offline = "offline"
    dealership = "dealership"

class SendData(BaseModel):
    amount: int = Field(..., alias="amount")
    customer_id: int = Field(..., alias="customerId")
    service_name: Services = Field(..., alias="serviceName")
    service_id: str = Field(..., alias="serviceId")
    customer_type: Optional[CustomerType] = Field("B2B", alias="customerType")

    @validator('amount')
    def check_amount(cls, amount):
        if amount < 10000:
            raise ValueError("must be greater than 10000 rial")
        return amount

    @validator("service_name")
    def check_service(cls, service):
        services = ["wallet", "order", "offline", "dealership"]
        if service not in services:
            raise ValueError("service name doesn't exist")
        return service

    # @validator('bank_name')
    # def check_bank_name(cls, bank):
    #     banks = ["melli", "mellat", "saman"]
    #     if bank.lower() not in banks:
    #         raise ValueError("bank name doesn't exist")
    #     return bank


class Payment(BaseModel):
    service_id: str = Field(..., alias="serviceId")
    customer_id: int = Field(..., alias="customerId")
    amount: str = Field(..., alias="amount")
    service_name: str = Field(..., alias="serviceName")
    bank_name: str = Field(default="mellat", alias="bankName")
    payment_type: str = Field(..., alias="paymentType")
    bank_code: str = Field(default="1011124", alias="bankCode")

    @validator("amount")
    def check_amount(cls, amount):
        if not str(amount).isdigit():
            raise HTTPException(status_code=422, detail={"error": "amount is wrong"})
        return str(int(amount) * 10)

    @validator("service_name")
    def check_service(cls, service):
        services = ["order"]
        if service not in services:
            raise HTTPException(status_code=422, detail={"error": "service name doesn't exist"})
        return service

    @validator('bank_name')
    def check_bank_name(cls, bank):
        banks = ["melli", "mellat", "saman"]
        if bank.lower() not in banks:
            raise HTTPException(status_code=422, detail={"error": "bank name doesn't exist"})
        return bank

    @validator("payment_type")
    def check_payment_type(cls, payment_type):
        payment_types = ["pos"]
        if payment_type not in payment_types:
            raise HTTPException(status_code=422, detail={"error": "payment type doesn't exist"})
        return payment_type
