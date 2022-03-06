from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel, validator, Field


class CreateParent(BaseModel):
    system_code: str = Field(
        ..., title="شناسه محصول", maxLength=11, minLength=11, placeholder="10010402101", isRequired=True,
        alias="systemCode"
    )
    name: Optional[str] = Field(
        None, title="نام", minLength=3, maxLength=256, placeholder="ردمی ۹ سی", isRequired=False
    )
    visible_in_site: bool = Field(..., title="نمایش در سایت", isRequired=True, alias="visibleInSite")

    @validator('system_code')
    def system_code_validator(cls, value):
        if not isinstance(value, str):
            raise HTTPException(status_code=417, detail={
                "error": "system code must be a string",
                "label": "کد سیستمی باید از نوع رشته باشد"
            })
        elif len(value) != 11:
            raise HTTPException(status_code=417, detail={
                "error": "system_code must be 11 characters",
                "label": "طول شناسه محصول باید ۱۱ کاراکتر باشد"
            })
        return value

    @validator('name')
    def name_validator(cls, value):
        if not isinstance(value, str):
            raise HTTPException(status_code=417, detail={
                "error": 'name must be a string',
                "label": "اسم باید از نوع رشته باشد"
            })
        elif len(value) < 3 or len(value) > 256:
            raise HTTPException(status_code=417, detail={
                "error": "name must be between 3 and 256 characters",
                "label": "طول اسم باید میان ۳ تا ۲۵۶ کاراکتر باشد"
            })
        return value

    @validator('visible_in_site')
    def visible_in_site_validator(cls, value):
        if not isinstance(value, bool):
            raise HTTPException(status_code=417, detail={
                "error": 'visible_in_site must be a boolean',
                "label": "نمایش در سایت باید از نوع بولی باشد"
            })
        return value


class CreateChild(BaseModel):
    parent_system_code: str = Field(
        ..., title="شناسه اصلی محصول", maxLength=11, minLength=11, placeholder="10010402101", isRequired=True, alias="parentSystemCode"
    )
    system_code: str = Field(
        ..., title="شناسه محصول", maxLength=12, minLength=12, placeholder="100104021006", isRequired=True, alias="systemCode"
    )
    visible_in_site: bool = Field(..., title="نمایش در سایت", isRequired=True, alias="visibleInSite")

    @validator('system_code')
    def system_code_validator(cls, value):
        if not isinstance(value, str):
            raise HTTPException(status_code=417, detail={
                "error": "system codes must be a string",
                "label": "شناسه های محصولات باید از نوع رشته باشد"
            })
        elif len(value) != 12:
            raise HTTPException(status_code=417, detail={
                "error": "system_code must be 12 characters",
                "label": "طول شناسه محصول باید ۱۲ کاراکتر باشد"
            })
        return value

    @validator('visible_in_site')
    def visible_in_site_validator(cls, value):
        if not isinstance(value, bool):
            raise HTTPException(status_code=417, detail={
                "error": 'visible_in_site must be a boolean',
                "label": "نمایش در سایت باید از نوع بولی باشد"
            })
        return value


class AddAtributes(BaseModel):
    system_code: str = Field(
        ..., title="شناسه محصول", maxLength=12, minLength=12, placeholder="100104021006", isRequired=True, alias="systemCode"
    )
    attributes: dict
