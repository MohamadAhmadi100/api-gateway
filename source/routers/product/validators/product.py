from typing import Optional, List

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
    url_name: Optional[str] = Field(..., title="لینک", minLength=3, maxLength=256, isRequired=True,
                                    alias="urlName")

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

    @validator('url_name')
    def url_name_validator(cls, value):
        if not isinstance(value, str):
            raise HTTPException(status_code=417, detail={
                "error": 'url_name must be a string',
                "label": "لینک باید از نوع رشته باشد"
            })
        elif len(value) < 3 or len(value) > 256:
            raise HTTPException(status_code=417, detail={
                "error": "url_name must be between 3 and 256 characters",
                "label": "طول لینک باید میان ۳ تا ۲۵۶ کاراکتر باشد"
            })
        return value


class CreateChild(BaseModel):
    parent_system_code: str = Field(
        ..., title="شناسه اصلی محصول", maxLength=11, minLength=11, placeholder="10010402101", isRequired=True,
        alias="parentSystemCode"
    )
    system_code: str = Field(
        ..., title="شناسه محصول", maxLength=12, minLength=12, placeholder="100104021006", isRequired=True,
        alias="systemCode"
    )

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


class AddAttributes(BaseModel):
    system_code: str = Field(
        ..., title="شناسه محصول", maxLength=12, minLength=12, placeholder="100104021006", isRequired=True,
        alias="systemCode"
    )
    attributes: dict


class EditProduct(BaseModel):
    visible_in_site: bool = Field(..., title="نمایش در سایت", isRequired=True, alias="visibleInSite")

    @validator('visible_in_site')
    def visible_in_site_validator(cls, value):
        if not isinstance(value, bool):
            raise HTTPException(status_code=417, detail={
                "error": "visible_in_site must be a boolean",
                "label": "نمایش در سایت باید از نوع بولین باشد"
            })
        return value


class KowsarCustomCategory(BaseModel):
    system_code: str = Field(..., title="شناسه محصول", maxLength=12, minLength=12, placeholder="100104021006",
                             isRequired=True,
                             alias="systemCode")
    custom_name: Optional[str] = Field(..., title="نام محصول", maxLength=256, minLength=3, placeholder="محصول سفارشی",
                                       isRequired=True,
                                       alias="customName")
    visible_in_site: bool = Field(..., title="نمایش در سایت", isRequired=True, alias="visibleInSite")

    image: Optional[str] = Field(..., title="تصویر محصول", maxLength=256, minLength=3, placeholder="تصویر محصول",
                                 isRequired=False)

    @validator('visible_in_site')
    def visible_in_site_validator(cls, value):
        if not isinstance(value, bool):
            raise HTTPException(status_code=417, detail={
                "error": "visible_in_site must be a boolean",
                "label": "نمایش در سایت باید از نوع بولین باشد"
            })
        return value

    @validator('custom_name')
    def custom_name_validator(cls, value):
        if not isinstance(value, str):
            raise HTTPException(status_code=417, detail={
                "error": "custom_name must be a string",
                "label": "نام محصول سفارشی باید از نوع رشته باشد"
            })
        elif len(value) < 3:
            raise HTTPException(status_code=417, detail={
                "error": "custom_name must be at least 3 characters",
                "label": "طول نام محصول سفارشی باید حداقل ۳ کاراکتر باشد"
            })
        elif len(value) > 256:
            raise HTTPException(status_code=417, detail={
                "error": "custom_name must be at most 256 characters",
                "label": "طول نام محصول سفارشی باید حداکثر ۲۵۶ کاراکتر باشد"
            })
        return value

    @validator('system_code')
    def system_code_validator(cls, value):
        if not isinstance(value, str):
            raise HTTPException(status_code=417, detail={
                "error": "system_code must be a string",
                "label": "شناسه محصول باید از نوع رشته باشد"
            })
        return value

    @validator('image')
    def image_validator(cls, value):
        if not isinstance(value, str):
            raise HTTPException(status_code=417, detail={
                "error": "image must be a string",
                "label": "تصویر محصول باید از نوع رشته باشد"
            })
        return value


class CustomCategory(BaseModel):
    name: str
    products: List[str]
    visible_in_site: bool
    image: Optional[str]

    @validator('name')
    def name_validator(cls, value):
        if not isinstance(value, str):
            raise HTTPException(status_code=417, detail={
                "error": "name must be a string",
                "label": "نام باید از نوع رشته باشد"
            })
        elif len(value) < 3:
            raise HTTPException(status_code=417, detail={
                "error": "name must be at least 3 characters",
                "label": "طول نام باید حداقل ۳ کاراکتر باشد"
            })
        elif len(value) > 256:
            raise HTTPException(status_code=417, detail={
                "error": "name must be at most 256 characters",
                "label": "طول نام باید حداکثر ۲۵۶ کاراکتر باشد"
            })
        return value

    @validator('products')
    def products_validator(cls, value):
        if not isinstance(value, list):
            raise HTTPException(status_code=417, detail={
                "error": "products must be a list",
                "label": "لیست محصولات باید از نوع لیست باشد"
            })
        for item in value:
            if not isinstance(item, str):
                raise HTTPException(status_code=417, detail={
                    "error": "products must be a list of strings",
                    "label": "لیست محصولات باید از نوع لیست رشته باشد"
                })
            elif len(item) != 25:

                raise HTTPException(status_code=417, detail={
                    "error": "products must be a list of 25-character strings",
                    "label": "لیست محصولات باید از نوع لیست رشته با طول ۲۵ کاراکتر باشد"
                })
        return value

    @validator('visible_in_site')
    def visible_in_site_validator(cls, value):
        if not isinstance(value, bool):
            raise HTTPException(status_code=417, detail={
                "error": "visible_in_site must be a boolean",
                "label": "مقدار visible_in_site باید از نوع رشته باشد"
            })
        return value

    @validator('image')
    def image_validator(cls, value):
        if not isinstance(value, str):
            raise HTTPException(status_code=417, detail={
                "error": "image must be a string",
                "label": "تصویر باید از نوع رشته باشد"
            })
        return value


class Product(BaseModel):
    system_codes: list = Field(..., maxLength=11, minLength=11, isRequired=True, alias="systemCodes")
    name: Optional[str] = Field(None, minLength=3, maxLength=256, isRequired=False)
    url_name: Optional[str] = Field(..., minLength=3, maxLength=256, isRequired=True, alias="urlName")

    @validator('system_codes')
    def system_codes_validator(cls, value):
        if not isinstance(value, list):
            raise HTTPException(status_code=417, detail={
                "error": "system_codes must be a list",
                "label": "لیست شناسه های محصول باید از نوع لیست باشد"
            })
        for item in value:
            if not isinstance(item, str):
                raise HTTPException(status_code=417, detail={
                    "error": "system_codes must be a list of strings",
                    "label": "لیست شناسه های محصول باید از نوع لیست رشته باشد"
                })
        return value

    @validator('url_name')
    def url_name_validator(cls, value):
        if not isinstance(value, str):
            raise HTTPException(status_code=417, detail={
                "error": "url_name must be a string",
                "label": "نام باید از نوع رشته باشد"
            })
        elif len(value) < 3:
            raise HTTPException(status_code=417, detail={
                "error": "url_name must be at least 3 characters",
                "label": "طول نام باید حداقل ۳ کاراکتر باشد"
            })
        elif len(value) > 256:
            raise HTTPException(status_code=417, detail={
                "error": "url_name must be at most 256 characters",
                "label": "طول نام باید حداکثر ۲۵۶ کاراکتر باشد"
            })
        return value

    @validator('name')
    def name_validator(cls, value):
        if not isinstance(value, str):
            raise HTTPException(status_code=417, detail={
                "error": "name must be a string",
                "label": "نام باید از نوع رشته باشد"
            })
        elif len(value) < 3:
            raise HTTPException(status_code=417, detail={
                "error": "name must be at least 3 characters",
                "label": "طول نام باید حداقل ۳ کاراکتر باشد"
            })
        elif len(value) > 256:
            raise HTTPException(status_code=417, detail={
                "error": "name must be at most 256 characters",
                "label": "طول نام باید حداکثر ۲۵۶ کاراکتر باشد"
            })
        return value
