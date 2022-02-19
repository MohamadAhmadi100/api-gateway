from pydantic import BaseModel, validator, Field


class GetUrl(BaseModel):
    amount: str = Field(...)
    bank_name: str = Field(...)
    customer_id: str = Field(...)

    @validator('amount')
    def check_amount(cls, v):
        """
        amount should be numeric
        """
        if not v.isalnum():
            raise ValueError('must be alphanumeric')

        if int(v) < 10000:
            raise ValueError("must be greater than 5000 toman")
        return v

    @validator('bank_name')
    def check_bank_name(cls, v):
        """
        bank name should exist in banks
        """
        banks = ["melli", "mellat", "saman"]
        if v.lower() not in banks:
            raise ValueError("bank name doesn't exist")
        return v

    @validator("customer_id")
    def check_customer_id(cls, v):
        """
        customer id must be int
        """
        if not v.isalnum():
            raise ValueError('must be alphanumeric')
        return v.title()
