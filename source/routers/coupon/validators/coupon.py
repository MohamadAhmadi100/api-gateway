from enum import Enum
from typing import List, Optional

from fastapi import HTTPException
from pydantic import BaseModel, validator, Field


class Coupon(BaseModel):
    token: str = Field(
        title="کد تخفیف",
        alias="token",
        name="token",
        description="token",
        dataType="int",
        type="Id",
        isRequired=True
    )

    @validator("token")
    def system_code_validator(cls, value):
        if not isinstance(value, str):
            raise HTTPException(status_code=422, detail="لطفا کد تخفیف را به درستی وارد کنید")
        if len(value) < 8 or len(value) > 11:
            raise HTTPException(status_code=422, detail="کد تخفیف وارد شده نادرست است")
        if ";" in value:
            raise HTTPException(status_code=422, detail="لطفا کد تخفیف را به درستی وارد کنید")
        if "-" not in value:
            raise HTTPException(status_code=422, detail="لطفا کد تخفیف را به درستی وارد کنید")
        return value
