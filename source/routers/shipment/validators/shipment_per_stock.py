
from pydantic import BaseModel, Field
from typing import List, Optional



class PerStock(BaseModel):
    method: str = Field(isRequired=True)
    insurance: dict
    transferee: Optional[dict]
