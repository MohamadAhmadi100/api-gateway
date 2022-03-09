import re
from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel, validator,Field


VALID_COUPON_TYPE = [
    'customer', 'public', 'product', 'event', 'customer-event', 'customer-product','event-product', 'customer-product-event']

VALID_VALUE_TYPE = ['percent', 'value']
class Coupon(BaseModel):
    title: str = Field(
                     ..., title = "اسم کوپن", maxLength = 16, minLength = 2, isRequired = True ,alias="title")

    code_length: Optional[int] = Field(
        4, title="تعداد حروف کد", minLength=1, maxLength=6, isRequired=False, alias="codeLength"
    )
    created_time: Optional[str]= Field(
        None, title="زمان ایجاد کوپن", minLength=10, maxLength=10, isRequired=False
    )

    started_at: Optional[str]=Field(
        None, title="زمان شروع تخفیف", minLength=10, maxLength=10, isRequired=False
    )

    expire_time: str=Field(
        None, title="زمان پایان تخفیف", minLength=10, maxLength=10, isRequired=True, alias="expireTime"
    )
    has_expire: bool = Field(
        None, title="انقضای تخفیف", isRequired=True, alias="hasExpire"
    )
    count: int= Field(
        None, title="تعداد کل کوپن", minLength=1, maxLength=6, isRequired=True ,alias="count"
    )
    assign_customers: list= Field(
        None, title="مشتری های دارای کوپن", isRequired=True ,alias="assignCustomers"
    )
    user_limit: Optional[int] = Field(
        None, title="تعداد مجاز", minLength=1, maxLength=6, isRequired=False, alias="userLimit"
    )
    assign_customer_groups: Optional[list] = Field(
        None, title="گروه مشتری های تخفیف دار", isRequired=False, alias="assignCustomerGroups"
    )
    min_order_price: Optional[int] = Field(
        None, title="حداقل قیمت",  minLength=1, maxLength=6,isRequired=False, alias="minOrderPrice"
    )
    min_order: Optional[int] = Field(
        None, title="حداقل سفارش",minLength=1, maxLength=6, isRequired=False, alias="minOrder"
    )
    item_count: Optional[int] = Field(
        None, title="تعداد هر آیتم", minLength=1, maxLength=6, isRequired=False,alias="itemCount"
    )
    value: int = Field(
        None, title="میزان تخفیف", isRequired=True,alias="value"
    )
    max_value: int = Field(
        None, title="حداکثر تخفیف", isRequired=True, alias="maxValue"
    )
    value_type: int = Field(
        None, title="نوع تخفیف", isRequired=True , alias="valueType"
    )
    is_enabled: bool = Field(
        None, title="فعال بودن کوپن",  isRequired=True , alias="isEnabled"
    )
    coupon_codes: Optional[list] = Field(
        None, title="کوپن کدها", minLength=2, maxLength=64, isRequired=True
    )
    prefix: Optional[str] = Field(
        None, title="پیشوند کد", minLength=2, maxLength=8, isRequired=False, alias="prefix"
    )
    suffix: Optional[str] = Field(
        None, title="پسوند کد", minLength=2, maxLength=8, isRequired=False,  alias="suffix"
    )
    assigned_product: Optional[list] = Field(
        None, title="محصولات تخفیف دار", minLength=1, maxLength=1000, isRequired=False,  alias="assignedProduct"
    )
    assigned_events: Optional[list] = Field(
        None, title="رویدادهای تخفیف دار",  isRequired=True , alias="assignedEvent"
    )
    coupon_types: int = Field(
        None, title="نوع کوپن", isRequired=True,  alias="couponTypes"
    )
    used_count: Optional[dict] = Field(
        None, title="تعداد استفاده شده", isRequired=False,  alias="usedCount"
    )
    fixed_name: Optional[bool] = Field(
        None, title="نام ثابت", isRequired=False , alias="fixedName"
    )

    @validator('coupon_types')
    def coupon_types_validator(cls, value):
        if not isinstance(value, int):
            raise ValueError('coupon_type must be integer')
        elif 0 >= value or value > len(VALID_COUPON_TYPE):
            raise ValueError(f'coupon_types should be between 0 and {len(VALID_COUPON_TYPE)-1}')
        return VALID_COUPON_TYPE[value]

    @validator("title")
    def title_validator(cls, value):
        if not isinstance(value, str):
            raise HTTPException(status_code=422, detail={"error": "title must be a string"})
        elif 2 >= len(value) or len(value) > 256:
            raise HTTPException(status_code=422, detail={"error": "title must be between 2 and 256 characters"})
        return value

    @validator("created_time")
    def created_time_validator(cls, value):
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
    def expire_time_validator(cls, value):
        pattern = r"^1[34][0-9][0-9]-(0?[1-9]|1[012])-(0?[1-9]|[12][0-9]|3[01])$"
        match = re.fullmatch(pattern, value)
        if not match:
            raise HTTPException(status_code=422, detail={"error": "Please enter a valid date"})
        return value

    @validator("count")
    def count_validator(cls, value):
        if not isinstance(value, int):
            raise HTTPException(status_code=422, detail={"error": "count must be a integer"})
        return value

    @validator("assign_customers")
    def assign_customers_validator(cls, value):
        if not isinstance(value, list):
            # for item in value:
            #     if not isinstance(item, int):
            #         raise HTTPException(status_code=422, detail={"error": "customer_ID must be an int"})
            #     return value
            raise HTTPException(status_code=422, detail={"error": "assign_customers must be a list"})
        return value

    @validator("user_limit")
    def user_limit_validator(cls, value):
        if not isinstance(value, int):
            raise HTTPException(status_code=422, detail={"error": "user_limit must be a integer"})
        return value

    @validator("assign_customer_groups")
    def assign_customer_groups_validator(cls, value):
        if not isinstance(value, list):
            # for item in value:
            #     if not isinstance(item, int):
            #         raise HTTPException(status_code=422, detail={"error": "customer_ID must be an int"})
            #     return value
            raise HTTPException(status_code=422, detail={"error": "assign_customer_groups must be a list"})
        return value

    @validator("min_order_price")
    def min_order_price_validator(cls, value):
        if not isinstance(value, int):
            raise HTTPException(status_code=422, detail={"error": "min_order_price must be a integer"})
        return value

    @validator("min_order")
    def min_order_validator(cls, coupon_min_order):
        pass

    @validator("item_count")
    def item_count_validator(cls, value):
        if not isinstance(value, int):
            raise HTTPException(status_code=422, detail={"error": "item_count must be a integer"})
        return value

    @validator("value")
    def value_validator(cls, value):
        if not isinstance(value, int):
            raise HTTPException(status_code=422, detail={"error": "value must be a integer"})
        return value

    @validator("max_value")
    def max_value_validator(cls, value):
        if not isinstance(value, int):
            raise HTTPException(status_code=422, detail={"error": "max_value must be a integer"})
        return value

    @validator("value_type")
    def value_type_validator(cls, value):
        if not isinstance(value, int):
            raise ValueError('value_type must be integer')
        elif 0 >= value or value > len(VALID_VALUE_TYPE):
            raise ValueError(f'value_types should be between 0 and {len(VALID_VALUE_TYPE)-1}')
        return VALID_VALUE_TYPE[value]

    @validator("is_enabled")
    def is_enabled_validator(cls, value):
        if not isinstance(value, bool):
            raise HTTPException(status_code=417, detail={"error": "is_enabled must be boolean"})

    @validator("coupon_codes")
    def coupon_codes_validator(cls, coupon_coupon_codes):
        if not isinstance(coupon_coupon_codes, list):
            raise HTTPException(status_code=417, detail={"coupon_codes must be list"})


    @validator("prefix")
    def prefix_validator(cls, value):
        pattern = r"^[A-Za-z0-9]{2,8}$"
        match = re.fullmatch(pattern, value)
        if not match:
            raise HTTPException(status_code=422, detail={"error": "Please enter a valid prefix"})
        return value

    @validator("suffix")
    def suffix_validator(cls, value):
        pattern = r"^[A-Za-z0-9]{2,8}$"
        match = re.fullmatch(pattern, value)
        if not match:
            raise HTTPException(status_code=422, detail={"error": "Please enter a valid suffix"})
        return value

    @validator("assigned_product")
    def assigned_product_validator(cls, value):
        if not isinstance(value, list):
            raise HTTPException(status_code=422, detail={"error": "assigned_product must be a list"})
        return value

    @validator("assigned_events")
    def assigned_events_validator(cls, value):
        if not isinstance(value, list):
            raise HTTPException(status_code=422, detail={"error": "assigned_events must be a list"})
        return value

    @validator("used_count")
    def used_count_validator(cls, value):
        if not isinstance(value, dict):
            raise HTTPException(status_code=422, detail={"error": "used_count must be a dictionary"})
        return value

    @validator("fixed_name")
    def fixed_name_validator(cls, value):
        if not isinstance(value, bool):
            raise HTTPException(status_code=417, detail={"error": "fixed_name must be boolean"})



class RequestBody(BaseModel):

    coupon_ID: str = Field(
        None, title="کد تخفیف", isRequired=True, alias="couponID"
    )

    customer_ID: int = Field(
        None, title="شناسه مشتری", minLength=11, maxLength=11, isRequired=True, alias="customerID"
    )

    product_name: str = Field(
        ..., title="شناسه محصول", maxLength=11, minLength=11, isRequired=True,
        alias="productName"
    )

    total_price: Optional[int] = Field(
        None, title="قیمت کل" , minLength=2, maxLength=32,  isRequired=False, alias="totalPrice"
    )

    item_count: Optional[int] = Field(
        None, title="تعداد محصول", minLength=1, maxLength=5, isRequired=False, alias="itemCount"
    )

    event: Optional[str] = Field(
        None, title="رویداد", minLength=1, maxLength=256, isRequired=False, alias="event"
    )

    @validator("coupon_ID")
    def validate_coupon_id(cls, value):
        if not isinstance(value, str):
            raise HTTPException(status_code=422, detail={"error": "coupon_ID must be string"})
        return value

    @validator("customer_ID")
    def customer_id_validator(cls, value):
        if not isinstance(value, int):
            raise HTTPException(status_code=422, detail={"error": "customer_ID must be integer"})
        return value

    @validator('product_name')
    def product_name_validator(cls, value):
        if not isinstance(value, str):
            raise HTTPException(status_code=417, detail={"error": " product_name must be string"})

    @validator("total_price")
    def total_priceـvalidator(cls, value):
        if not isinstance(value, int):
            raise HTTPException(status_code=422, detail={"error": "total_price must be  integer"})
        return value

    @validator("item_count")
    def item_countـvalidator(cls, value):
        if not isinstance(value, int):
            raise HTTPException(status_code=422, detail={"error": "item_count must be integer"})
        return value

    @validator('event')
    def event_validator(cls, value):
        if not isinstance(value, str):
            raise HTTPException(status_code=417, detail={"error": " event must be string"})
        return value
