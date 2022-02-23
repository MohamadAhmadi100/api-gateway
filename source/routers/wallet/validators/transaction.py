from enum import Enum
from pydantic import BaseModel, Field, validator
from typing import Optional


class SortName(str, Enum):
    customer_id = "customerId"
    order_number = "customerNumber"
    payment_id = "paymentID"
    payment_date = "paymentDate"
    amount = "amount"
    wallet_id = "walletID"
    user_id = "userId"
    transaction_date = "transactionDate"
    create_date = "createDate"
    transaction_id = "transactionId"


class SortType(str, Enum):
    asc = "asc"
    desc = "desc"


class Transaction(BaseModel):
    page: Optional[int] = Field(alias="page", default=1)
    sort_name: Optional[SortName] = Field(alias="sortName", default="customerId")
    sort_type: Optional[SortType] = Field(alias="sortType", default="desc")
    per_page: Optional[int] = Field(alias="perPage", default=15)
    search: Optional[str] = Field(alias="search", default=None)
    filters: Optional[list] = Field(alias="filters", default=list())
    ranges: Optional[list] = Field(alias="ranges", default=list())

    @validator("filters")
    def check_filters(cls, v):
        if v is not None:
            for i in v:
                if len(i.keys()) != 2:
                    raise ValueError("filter is not valid")
                elif "name" not in i.keys():
                    raise ValueError("name doesnt exist in filter")
                elif "value" not in i.keys():
                    raise ValueError("value doesnt exist in filter")
            return v
        return None

    @validator("ranges")
    def check_ranges(cls, v):
        if v is not False:
            for i in v:
                if len(i) != 2:
                    raise ValueError("filter is not valid")
                elif "name" not in i.keys():
                    raise ValueError("name doesnt exist in filter")
                elif "value" not in i.keys():
                    raise ValueError("value doesnt exist in filter")
                elif "min" not in i["value"]:
                    raise ValueError("value doesnt have min")
                elif "max" not in i["value"]:
                    raise ValueError("value doesnt have max")
            return v
        return None

