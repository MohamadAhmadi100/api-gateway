
from pydantic import BaseModel
from typing import List


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
    stocks: List[Stock]
