from pydantic import BaseModel, validator, Field


class SendData(BaseModel):
    amount: int = Field(..., alias="amount")
    customer_id: int = Field(..., alias="customerId")
    service_name: str = Field(..., alias="serviceName")
    service_id: str = Field(..., alias="serviceId")

    @validator('amount')
    def check_amount(cls, amount):
        if amount < 10000:
            raise ValueError("must be greater than 10000 rial")
        return amount

    @validator("service_name")
    def check_service(cls, service):
        services = ["wallet", "order", "offline", "controllers"]
        if service not in services:
            raise ValueError("service name doesn't exist")
        return service

    # @validator('bank_name')
    # def check_bank_name(cls, bank):
    #     banks = ["melli", "mellat", "saman"]
    #     if bank.lower() not in banks:
    #         raise ValueError("bank name doesn't exist")
    #     return bank
