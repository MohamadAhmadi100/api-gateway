import re

from fastapi import HTTPException
from pydantic import BaseModel, Field, validator



class Address(BaseModel):
    customer_name: str = Field(alias="customerName")
    state_name: str = Field(alias="stateName")
    state_id: str = Field(alias="stateId")
    city_id: str = Field(alias="cityId")
    city_name: str = Field(alias="cityName")
    region_code: str = Field(alias="regionCode")
    street: str = Field(alias="street")
    alley: str = Field(alias="alley")
    plaque: str = Field(alias="plaque")
    unit: str = Field(alias="unit")
    tel: str = Field(alias="tel")
    postal_code: str = Field(alias="postalCode")
    is_default: bool = Field(alias="isDefault")

    @validator("customer_name")
    def validate_customer_name(cls, customer_name):
        pattern = r"[ ]{0,1}[\u0600-\u06FF]{2,32}$"
        match = re.findall(pattern, customer_name)
        if not match:
            raise HTTPException(status_code=422, detail={"error": "نام وارد شده معتبر نیست"})
        return customer_name

    @validator("state_name")
    def validate_customer_state_name(cls, state_name):
        pattern = r"[ ]{0,1}[\u0600-\u06FF]{2,32}$"
        match = re.findall(pattern, state_name)
        if not match:
            raise HTTPException(status_code=422, detail={"error": "استان وارد شده معتبر نیست."})
        return state_name

    @validator("state_id")
    def validate_customer_state_id(cls, state_id):
        pattern = r"^[0-9]{2,6}$"
        match = re.fullmatch(pattern, state_id)
        if not match:
            raise HTTPException(status_code=422, detail={"error": "Please enter a valid state id"})
        return state_id

    @validator("city_id")
    def validate_customer_city_id(cls, city_id):
        pattern = r"^[0-9]{2,6}$"
        match = re.fullmatch(pattern, city_id)
        if not match:
            raise HTTPException(status_code=422, detail={"error": "Please enter a valid city id"})
        return city_id

    @validator("city_name")
    def validate_customer_city_name(cls, city_name):
        pattern = r"[ ]{0,1}[\u0600-\u06FF]{2,32}$"
        match = re.findall(pattern, city_name)
        if not match:
            raise HTTPException(status_code=422, detail={"error": "شهر وارد شده معتبر نیست."})
        return city_name

    @validator("street")
    def validate_street(cls, street):
        pattern = r"[ ]{0,5}[\u0600-\u06FF]{2,32}$"
        match = re.findall(pattern, street)
        if not match:
            raise HTTPException(status_code=422, detail={"error": "نام خیابان وارد شده معتبر نیست."})
        return street

    @validator("alley")
    def validate_alley(cls, alley):
        pattern = r"[ ]{0,1}[\u0600-\u06FF]{2,32}$"
        match = re.findall(pattern, alley)
        if not match:
            raise HTTPException(status_code=422, detail={"error": "نام کوچه وارد شده معتبر نیست."})
        return alley

    @validator("plaque")
    def validate_plaque(cls, plaque):
        pattern = r"^[0-9]{1,6}$"
        match = re.fullmatch(pattern, plaque)
        if not match:
            raise HTTPException(status_code=422, detail={"error": "پلاک وارد شده معتبر نیست."})
        return plaque

    @validator("unit")
    def validate_unit(cls, unit):
        pattern = r"^[0-9]{1,6}$"
        match = re.fullmatch(pattern, unit)
        if not match:
            raise HTTPException(status_code=422, detail={"error": "واحد وارد شده معتبر نیست."})
        return unit

    @validator("tel")
    def validate_tel(cls, tel):
        pattern = r"^[0-9]{11}$"
        match = re.fullmatch(pattern, tel)
        if not match:
            raise HTTPException(status_code=422, detail={"error": "شماره تماس وارد شده معتبر نیست."})
        return tel

    @validator("is_default")
    def validate_is_default(cls, is_default):
        print(is_default)
        if is_default not in [False, True]:
            raise HTTPException(status_code=422, detail={"error": "Please enter a valid is_default"})
        return is_default





class AddressId(BaseModel):
    address_id: int = Field(alias="addressId")