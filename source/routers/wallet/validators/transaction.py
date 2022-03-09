from enum import Enum
from pydantic import BaseModel, Field, BaseConfig, validator
from typing import Optional
from fastapi import Query


def make_enum(name, values):
    _k = _v = None

    class DictEnum(Enum):
        nonlocal _k, _v
        for _k, _v in values.items():
            locals()[_k] = _v

    DictEnum.__name__ = name
    return DictEnum


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
    filters: Optional[list] = Field(alias="filters", default=None)
    ranges: Optional[list] = Field(alias="ranges", default=None)

    class Config:
        orm_mode = True

    @validator("filters")
    def check_filters(cls, filters):
        if filters:
            try:
                filters = dict(filters)
                print(filters)
            except:
                for item in filters:
                    if len(item.keys()) != 2:
                        raise ValueError("فیلتر به درستی وارد نشده است")
                    elif "name" not in item.keys():
                        raise ValueError("فیلتر باید دارای نام باشد")
                    elif "value" not in item.keys():
                        raise ValueError("مقدار فیلتر مشخص نشده است")
            return filters

    @validator("ranges")
    def check_ranges(cls, ranges):
        if ranges:
            for i in ranges:
                if len(i) != 2:
                    raise ValueError("filter is not valid")  # todo: edit messages to persian
                elif "name" not in i.keys():
                    raise ValueError("name doesn't exist in filter")  # todo: edit messages to persian
                elif "value" not in i.keys():
                    raise ValueError("value doesn't exist in filter")  # todo: edit messages to persian
                elif "min" not in i["value"]:
                    raise ValueError("value doesn't have min")  # todo: edit messages to persian
                elif "max" not in i["value"]:
                    raise ValueError("value doesn't have max")  # todo: edit messages to persian
            return ranges
        return None
