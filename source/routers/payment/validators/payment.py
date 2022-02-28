from pydantic import BaseModel, validator, Field


class SendData(BaseModel):
    amount: str = Field(..., alias="amount")
    bank_name: str = Field(..., alias="bankName")
    customer_id: str = Field(..., alias="customerId")
    service: dict = Field(..., alias="serviceName")
    order_id: int = Field(..., alias="orderId")

    @validator('amount')
    def check_amount(cls, amount):
        if not amount.isalnum():
            raise ValueError('must be alphanumeric')

        if int(amount) < 10000:
            raise ValueError("must be greater than 1000 toman")
        return amount

    @validator('bank_name')
    def check_bank_name(cls, bank):
        banks = ["melli", "mellat", "saman"]
        if bank.lower() not in banks:
            raise ValueError("bank name doesn't exist")
        return bank

    @validator("customer_id")
    def check_customer_id(cls, customer_id):
        if not customer_id.isalnum():
            raise ValueError('must be alphanumeric')
        return customer_id

    @validator("service")
    def check_service(cls, service):
        input_data = ["service_name", "service_function"]
        if service.keys() not in input_data:
            raise ValueError("input data is invalid")
        services = ["wallet", "order"]
        if service.get("service").lower() not in services:
            raise ValueError("service name doesn't exist")
        return service
