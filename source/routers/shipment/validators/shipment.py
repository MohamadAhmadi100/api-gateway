import re

from fastapi import HTTPException
from pydantic import BaseModel, Field, validator
from typing import List


class Stock(BaseModel):
    stock_name: str
    stock_id: str
    origin: str
    destination: str
    weight: int
    total_price: int
    total_item: int

class Shipment(BaseModel):
    customer_id: int
    stocks: List[Stock]
