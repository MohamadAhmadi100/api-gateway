
from pydantic import BaseModel
from typing import List, Optional


class Stock(BaseModel):
    stockName: str
    stockId: str
    origin: str
    destination: str
    weight: int
    totalPrice: int
    totalItem: int

class Shipment(BaseModel):
    customerId: int
    customerType: Optional[str]
    stocks: List[Stock]
