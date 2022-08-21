from typing import Optional, List

from fastapi import HTTPException
from pydantic import BaseModel, validator, Field


class StoragesModel(BaseModel):
    storage_id: str = Field(..., alias="storageId")
    regular: Optional[int] = Field(None)
    informal_price: Optional[dict] = Field(None, alias="informalPrice")
    special: Optional[int] = None
    special_from_date: Optional[str] = Field(None, alias='specialFromDate')
    special_to_date: Optional[str] = Field(None, alias='specialToDate')

    @validator("storage_id")
    def storage_id_validator(cls, value):
        if not isinstance(value, str):
            raise HTTPException(status_code=422, detail={"error": "storage_id must be str"})
        elif 255 < len(value) or len(value) < 1:
            raise HTTPException(status_code=422, detail={"error": "type must be between 1 and 255"})
        return value

    @validator("regular")
    def regular_validator(cls, value):
        if not isinstance(value, int):
            raise HTTPException(status_code=422, detail={"error": "regular must be int"})
        elif 100_000_000_000_000 < value or value < 1:
            raise HTTPException(status_code=422, detail={"error": "regular must be between 1 and 100_000_000_000_000"})
        return value

    @validator("special")
    def special_validator(cls, value):
        if not isinstance(value, int):
            raise HTTPException(status_code=422, detail={"error": "special must be int"})
        elif 100_000_000_000_000 < value or value < 1:
            raise HTTPException(status_code=422, detail={"error": "special must be between 1 and 100_000_000_000_000"})
        return value

    @validator('informal_price')
    def informal_validator(cls, value):
        if not isinstance(value, dict):
            raise HTTPException(status_code=422, detail={"error": "informal must be dict"})
        elif value.get("type") not in ['fixed', "incremental", 'percentage']:
            raise HTTPException(status_code=422,
                                detail={"error": "informal type must be fixed, incremental or percentage"})
        elif not isinstance(value.get("price"), int) or not isinstance(value.get("percentage"), int):
            raise HTTPException(status_code=422, detail={
                "error": "informal price/percentage for type {} must be int".format(value.get("type"))})
        return value

    @validator("special_from_date")
    def special_from_date_validator(cls, value):
        if not isinstance(value, str):
            raise HTTPException(status_code=422, detail={"error": "special_from_date must be str"})
        elif 100000000000000 < len(value) or len(value) < 1:
            raise HTTPException(status_code=422,
                                detail={"error": "special_from_date must be between 1 and 100000000000000"})
        return value

    @validator("special_to_date")
    def special_to_date_validator(cls, value):
        if not isinstance(value, str):
            raise HTTPException(status_code=422, detail={"error": "special_to_date must be str"})
        elif 100000000000000 < len(value) or len(value) < 1:
            raise HTTPException(status_code=422,
                                detail={"error": "special_to_date must be between 1 and 100000000000000"})
        return value

    def get(self) -> dict:
        return {
            'storage_id': self.storage_id,
            'regular': self.regular,
            'special': self.special,
            'special_from_date': self.special_from_date,
            'special_to_date': self.special_to_date
        }


class CustomerTypes(BaseModel):
    type: str
    storages: List[StoragesModel] = []

    @validator("type")
    def type_validator(cls, value):
        if not isinstance(value, str):
            raise HTTPException(status_code=422, detail={"error": "type must be str"})
        elif 255 < len(value) or len(value) < 1:
            raise HTTPException(status_code=422,
                                detail={"error": "type must be between 1 and 255"})
        return value

    @validator("storages")
    def storages_validator(cls, value):
        if not isinstance(value, list):
            raise HTTPException(status_code=422, detail={"error": "storages must be array"})
        elif 255 < len(value):
            raise HTTPException(status_code=422, detail={"error": "storages must be between 1 and 255"})
        return value

    def get(self) -> dict:
        return {
            'type': self.type,
            'storages': [storage.get() for storage in self.storages]
        }


class CustomerTypeModel(BaseModel):
    B2B: Optional[CustomerTypes] = {
        "type": "B2B",
    }
    B2C: Optional[CustomerTypes] = {
        "type": "B2C",
    }
    B2G: Optional[CustomerTypes] = {
        "type": "B2G",
    }


class Price(BaseModel):
    system_code: str = Field(..., alias='systemCode')
    customer_type: CustomerTypeModel = Field({}, alias='customerType')

    @validator("system_code")
    def system_code_validator(cls, value):
        if value is not None:
            if not isinstance(value, str):
                raise HTTPException(status_code=422, detail={"error": "system_code must be str"})
            elif 100000000000000 < len(value) or len(value) < 1:
                raise HTTPException(status_code=422,
                                    detail={"error": "system_code must be between 1 and 100000000000000"})
            return value

    class Config:
        schema_extra = {
            "example": {
                "systemCode": "2000010010001001001001001",
                "customerType":
                    {
                        "B2B": {
                            'type': 'B2B',
                            "storages": [
                                {
                                    "storageId": "0",
                                    "regular": 30000000,
                                    'informal': 33000000,
                                    "special": 22000000,
                                    "specialFromDate": "2020-01-01",
                                    "specialToDate": "2020-01-01"
                                },
                                {
                                    "storageId": "1",
                                    "regular": 60000000,
                                    'informal': 33000000,
                                    "special": 42000000,
                                    "specialFromDate": "2020-01-01",
                                    "specialToDate": "2020-01-01"
                                }
                            ]
                        }
                    }
            }
        }

    def get(self) -> dict:
        return {
            "system_code": self.system_code,
            'customer_type': self.customer_type.dict()
        }


class UpdatePrice(BaseModel):
    system_code: str = Field(..., alias='systemCode')
    customer_type: str = Field(..., alias='customerType')
    storage_id: str = Field(..., alias='storageId')
    regular: int
    informal_price: Optional[dict] = Field(None, alias="informalPrice")
    special: Optional[int] = None
    special_from_date: Optional[str] = Field(None, alias='specialFromDate')
    special_to_date: Optional[str] = Field(None, alias='specialToDate')

    @validator("system_code")
    def system_code_validator(cls, value):
        if value is not None:
            if not isinstance(value, str):
                raise HTTPException(status_code=422, detail={"error": "system_code must be str"})
            elif 25 != len(value):
                raise HTTPException(status_code=422,
                                    detail={"error": "system_code must be 25 characters"})
            return value

    @validator("customer_type")
    def customer_type_validator(cls, value):
        if value is not None:
            if not isinstance(value, str):
                raise HTTPException(status_code=422, detail={"error": "customer_type must be str"})
            elif 20 < len(value) or len(value) < 1:
                raise HTTPException(status_code=422,
                                    detail={"error": "customer_type must be between 1 and 20 characters"})
            return value

    @validator("storage_id")
    def storage_id_validator(cls, value):
        if value is not None:
            if not isinstance(value, str):
                raise HTTPException(status_code=422, detail={"error": "storage_id must be str"})
            elif 20 < len(value) or len(value) < 1:
                raise HTTPException(status_code=422,
                                    detail={"error": "storage_id must be between 1 and 20 characters"})
            return value

    @validator("regular")
    def regular_validator(cls, value):
        if value is not None:
            if not isinstance(value, int):
                raise HTTPException(status_code=422, detail={"error": "regular must be int"})
            elif value < 0 or value > 1000000000:
                raise HTTPException(status_code=422, detail={"error": "regular must be between 0 and 1000000000"})
            return value

    @validator("special")
    def special_validator(cls, value):
        if value is not None:
            if not isinstance(value, int):
                raise HTTPException(status_code=422, detail={"error": "special must be int"})
            elif value < 0 or value > 1000000000:
                raise HTTPException(status_code=422, detail={"error": "special must be between 0 and 1000000000"})
            return value

    @validator("special_from_date")
    def special_from_date_validator(cls, value):
        if value is not None:
            if not isinstance(value, str):
                raise HTTPException(status_code=422, detail={"error": "special_from_date must be str"})
            elif 100000000000000 < len(value) or len(value) < 1:
                raise HTTPException(status_code=422,
                                    detail={"error": "special_to_date must be between 1 and 100000000000000"})
            return value

    @validator("special_to_date")
    def special_to_date_validator(cls, value):
        if value is not None:
            if not isinstance(value, str):
                raise HTTPException(status_code=422, detail={"error": "special_to_date must be str"})
            elif 100000000000000 < len(value) or len(value) < 1:
                raise HTTPException(status_code=422,
                                    detail={"error": "special_to_date must be between 1 and 100000000000000"})
            return value

    @validator('informal_price')
    def informal_validator(cls, value):
        if not isinstance(value, dict):
            raise HTTPException(status_code=422, detail={"error": "informal must be dict"})
        elif value.get("type") not in ['fixed', "incremental", 'percentage']:
            raise HTTPException(status_code=422,
                                detail={"error": "informal type must be fixed, incremental or percentage"})

        elif value.get("type") in ['fixed', "incremental"] and not isinstance(value.get("price"), int):
            raise HTTPException(status_code=422, detail={"error": "informal price must be int"})

        elif value.get("type") == 'percentage' and not isinstance(value.get("percentage"), int):
            raise HTTPException(status_code=422, detail={"error": "informal percentage must be int"})
        return value

    class Config:
        schema_extra = {
            "example": {
                "systemCode": "2000010010001001001001001",
                "customerType": "B2B",
                "storageId": "1",
                "regular": 1000000000,
                "special": 50000000,
                "informalPrice": {
                    "type": "fixed",
                    "price": 1000000000,
                },
                "specialFromDate": "2019-01-01 00:00:00",
                "specialToDate": "2019-01-01 00:00:00"
            }
        }
