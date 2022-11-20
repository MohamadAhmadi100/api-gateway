
from pydantic import BaseModel, Field
from typing import List, Optional, Union


class Stock(BaseModel):
    stockName: str
    stockId: str
    origin: str
    destination: str
    # nbId: str | None = None
    weight: int
    totalPrice: int
    totalItem: int

class Shipment(BaseModel):
    customerId: int
    customerType: Optional[str]
    stocks: List[Stock]
