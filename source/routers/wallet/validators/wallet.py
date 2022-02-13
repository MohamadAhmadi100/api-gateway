from pydantic import BaseModel, Field


class Wallet(BaseModel):
    customer_id: int = Field(alias="customerId")
