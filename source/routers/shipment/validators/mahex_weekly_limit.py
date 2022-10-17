from pydantic import BaseModel
from typing import List


class WeekDays(BaseModel):
    Saturday: int
    Sunday: int
    Monday: int
    Tuesday: int
    Wednesday: int
    Thursday: int
    Friday: int