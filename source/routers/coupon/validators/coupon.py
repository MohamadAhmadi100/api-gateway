import re
from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel, validator,Field
from persiantools.jdatetime import JalaliDate

VALID_COUPON_TYPE = (
    'customer', 'public', 'product', 'event', 'customer-public', 'customer-event', 'customer-product', 'public-event',
    'public-product', 'event-product', 'customer-public-event', 'customer-product-event', 'public-event-product',
    'customer-public-product', 'customer-public-event-product')
today = JalaliDate.today()

class Coupon(BaseModel):
    title: str = Field(
                     ..., title = "اسم کوپن", maxLength = 16, minLength = 2, isRequired = True ,alias="title")



    created_time: Optional[str]= Field(
        None, title="", minLength=10, maxLength=10, isRequired=False
    )

    started_at: Optional[str]=Field(
        None, title="", minLength=10, maxLength=10, isRequired=False
    )

    expire_time: str=Field(
        None, title="", minLength=10, maxLength=10, isRequired=True, alias="expireTime"
    )
    has_expire: bool = Field(
        None, title="", isRequired=True, alias="hasExpire"
    )
    count: int= Field(
        None, title="", minLength=1, maxLength=1000, isRequired=True ,alias="count"
    )
    assign_customers: list= Field(
        None, title="", minLength=1, maxLength=1000, isRequired=True ,alias=""
    )
    user_limit: Optional[int] = Field(
        None, title="", minLength=1, maxLength=1000, isRequired=False, alias="userLimit"
    )
    assign_customer_groups: Optional[list] = Field(
        None, title="", minLength=1, maxLength=1000, isRequired=False, alias=""
    )
    min_order_price: Optional[int] = Field(
        None, title="",  isRequired=False, alias="minOrderPrice"
    )
    min_order: Optional[int] = Field(
        None, title="", isRequired=False, alias="minOrder"
    )
    item_count: Optional[int] = Field(
        None, title="", minLength=1, maxLength=1000, isRequired=False,alias="itemCount"
    )
    value: int = Field(
        None, title="", isRequired=True,alias="value"
    )
    max_value: int = Field(
        None, title="", isRequired=True, alias="maxValue"
    )
    value_type: int = Field(
        None, title="", isRequired=True , alias="valueType"
    )
    is_enabled: bool = Field(
        None, title="",  isRequired=True , alias="isEnabled"
    )
    coupon_codes: list = Field(
        None, title="", minLength=2, maxLength=64, isRequired=True
    )
    prefix: Optional[str] = Field(
        None, title="", minLength=2, maxLength=8, isRequired=False, alias="prefix"
    )
    suffix: Optional[str] = Field(
        None, title="", minLength=2, maxLength=8, isRequired=False,  alias="suffix"
    )
    assigned_product: Optional[list] = Field(
        None, title="", minLength=1, maxLength=1000, isRequired=False,  alias="assignedProduct"
    )
    assigned_events: list = Field(
        None, title="",  isRequired=True , alias="assignedEvent"
    )
    coupon_types: int = Field(
        None, title="", isRequired=True,  alias="couponTypes"
    )
    used_count: Optional[dict] = Field(
        None, title="", isRequired=False,  alias="usedCount"
    )
    fixed_name: Optional[bool] = Field(
        None, title="", isRequired=False , alias="fixedName"
    )

    @validator('coupon_types')
    def coupon_types_validator(cls, value):
        if not isinstance(value, int):
            raise ValueError('coupon_type must be integer')
        elif 0 >= value or value > len(VALID_COUPON_TYPE):
            raise ValueError(f'coupon_types should be between 1 and {len(VALID_COUPON_TYPE)}')
        return VALID_COUPON_TYPE[value - 1]

    @validator("title")
    def validate_title(cls, value):
        if not isinstance(value, str):
            raise HTTPException(status_code=422, detail={"error": "title must be a string"})
        elif 2 >= len(value) or len(value) > 16:
            raise HTTPException(status_code=422, detail={"error": "title must be between 2 and 16 characters"})
        return value

    @validator("created_time")
    def validate_created_time(cls, value):
        pattern = r"^1[34][0-9][0-9]-(0?[1-9]|1[012])-(0?[1-9]|[12][0-9]|3[01])$"
        match = re.fullmatch(pattern, value)
        if not match:
            raise HTTPException(status_code=422, detail={"error": "Please enter a valid date"})
        return value

    @validator("started_at")
    def validate_started_time(cls, value):
        pattern = r"^1[34][0-9][0-9]-(0?[1-9]|1[012])-(0?[1-9]|[12][0-9]|3[01])$"
        match = re.fullmatch(pattern, value)
        if not match:
            raise HTTPException(status_code=422, detail={"error": "Please enter a valid date"})
        return value

    @validator("expire_time")
    def validate_expire_time(cls, value):
        pattern = r"^1[34][0-9][0-9]-(0?[1-9]|1[012])-(0?[1-9]|[12][0-9]|3[01])$"
        match = re.fullmatch(pattern, value)
        if not match:
            raise HTTPException(status_code=422, detail={"error": "Please enter a valid date"})
        return value

    @validator("count")
    def validate_count(cls, value):
        if not isinstance(value, int):
            raise HTTPException(status_code=422, detail={"error": "count must be a integer"})
        return value

    @validator("assign_customers")
    def validate_assign_customers(cls, value):
        if not isinstance(value, list):
            raise HTTPException(status_code=422, detail={"error": "count must be a list"})
        return value

    @validator("user_limit")
    def validate_user_limit(cls, value):
        if not isinstance(value, int):
            raise HTTPException(status_code=422, detail={"error": "count must be a integer"})
        return value

    @validator("assign_customer_groups")
    def validate_assign_customer_groups(cls, value):
        if not isinstance(value, list):
            raise HTTPException(status_code=422, detail={"error": "count must be a list"})
        return value

    @validator("min_order_price")
    def validate_min_order_price(cls, value):
        if not isinstance(value, int):
            raise HTTPException(status_code=422, detail={"error": "min_order_price must be a integer"})
        return value

    @validator("min_order")
    def validate_min_order(cls, coupon_min_order):
        pass

    @validator("item_count")
    def validate_item_count(cls, value):
        if not isinstance(value, int):
            raise HTTPException(status_code=422, detail={"error": "item_count must be a integer"})
        return value

    @validator("value")
    def validate_value(cls, value):
        if not isinstance(value, int):
            raise HTTPException(status_code=422, detail={"error": "value must be a integer"})
        return value

    @validator("max_value")
    def validate_max_value(cls, value):
        if not isinstance(value, int):
            raise HTTPException(status_code=422, detail={"error": "max_value must be a integer"})
        return value

    @validator("value_type")
    def validate_value_type(cls, value):
        if not isinstance(value, str):
            raise HTTPException(status_code=422, detail={"error": "value_type must be a string"})
        return value

    @validator("is_enabled")
    def validate_is_enabled(cls, value):
        if not isinstance(value, bool):
            raise HTTPException(status_code=417, detail={"error": "is_enabled must be boolean"})

    @validator("coupon_codes")
    def validate_coupon_codes(cls, coupon_coupon_codes):
        if not isinstance(coupon_coupon_codes, list):
            raise HTTPException(status_code=417, detail={"... must be list"})


    @validator("prefix")
    def validate_prefix(cls, value):
        pattern = r"^[A-Za-z0-9]{2,8}$"
        match = re.fullmatch(pattern, value)
        if not match:
            raise HTTPException(status_code=422, detail={"error": "Please enter a valid prefix"})
        return value

    @validator("suffix")
    def validate_suffix(cls, value):
        pattern = r"^[A-Za-z0-9]{2,8}$"
        match = re.fullmatch(pattern, value)
        if not match:
            raise HTTPException(status_code=422, detail={"error": "Please enter a valid suffix"})
        return value

    @validator("assigned_product")
    def validate_assigned_product(cls, value):
        if not isinstance(value, list):
            raise HTTPException(status_code=422, detail={"error": "count must be a list"})
        return value

    @validator("assigned_events")
    def validate_assigned_events(cls, value):
        if not isinstance(value, list):
            raise HTTPException(status_code=422, detail={"error": "count must be a list"})
        return value

    @validator("assigned_events")
    def validate_used_count(cls, value):
        if not isinstance(value, dict):
            raise HTTPException(status_code=422, detail={"error": "count must be a dictionary"})
        return value

    @validator("fixed_name")
    def validate_fixed_name(cls, value):
        if not isinstance(value, bool):
            raise HTTPException(status_code=417, detail={"error": "fixed_name must be boolean"})
