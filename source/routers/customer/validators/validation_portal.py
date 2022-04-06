import re

from fastapi import HTTPException
from pydantic import BaseModel, validator, Field


class StaffAuth(BaseModel):
    filters: dict = Field(
        title="فیلترها",
        alias="filters",
        name="filters",
        placeholder="فیلترها",
        description="object for get customers data by filters",
        dataType="object",
        type="filter",
        isRquired=False
    )
