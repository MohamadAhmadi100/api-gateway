import re
from enum import Enum
from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel, validator, Field


class SortType(str, Enum):
    asc = "asc"
    desc = "desc"


class DateType(BaseModel):
    start: str = Field(
        placeholder="1401-01-17 11:25:00",
        type="jalali",
        example="1401-01-17 11:25:00"
    )
    end: str = Field(
        placeholder="1401-01-17 11:25:00",
        type="jalali",
        example="1401-01-18 23:25:00"
    )


class CustomerStatus(BaseModel):
    customerIsMobileConfirm: bool
    customerIsConfirm: bool
    customerIsActive: bool


class MultipleStatus(BaseModel):
    values: Optional[CustomerStatus]


class Filters(BaseModel):
    registerDate: Optional[DateType]
    lastOrderDate: Optional[DateType]
    status: Optional[MultipleStatus]


class StaffAuth(BaseModel):
    filters: Optional[Filters]
    page: Optional[int] = Field(
        title="صفحه",
        alias="page",
        name="page",
        description="object for executing records",
        dataType="object",
        type="filter",
        isRquired=False
    )
    perPage: Optional[int] = Field(
        title="تعداد در هر صفحه",
        alias="perPage",
        name="perPage",
        description="number of records showing in every single page",
        dataType="str",
        type="page",
        isRquired=False
    )
    sortType: Optional[SortType] = Field(
        title="ترتیب نمایش",
        alias="sortType",
        name="sortType",
        description="asc/desc sort type option",
        dataType="str",
        type="sortType",
        isRquired=False
    )
    sortName: Optional[str] = Field(
        title="نحوه مرتب سازی",
        alias="sortName",
        name="sortName",
        description="field name for sort records based on",
        dataType="str",
        type="sortName",
        isRquired=False
    )
    search: Optional[str] = Field(
        title="جست و جو",
        alias="search",
        name="search",
        description="thr phrase for search",
        dataType="str",
        type="search",
        isRquired=False
    )
