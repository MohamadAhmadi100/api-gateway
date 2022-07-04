from pydantic import BaseModel, Field, validator


class Charge(BaseModel):
    amount: int = Field(..., alias="amount")
    wallet_id: int = Field(..., alias="walletId")
    bank_name: str = Field(..., alias="bankName")
    customer_id: int = Field(..., alias="customerId")

    @validator('amount')
    def check_amount(cls, amount):
        if amount < 10000:
            raise ValueError("must be greater than 1000 rial")
        return amount
