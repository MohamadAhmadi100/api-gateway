from typing import Optional, List

from fastapi import HTTPException
from pydantic import BaseModel, validator

from source.routers.pricing.validators.storage_validator import StoragesModel


class CustomerTypes(BaseModel):
    type: str
    regular: int
    special: Optional[int] = None
    storages: List[StoragesModel] = []

    @validator("type")
    def type_validator(cls, value):
        if not isinstance(value, str):
            raise HTTPException(status_code=422, detail={"error": "type must be str"})
        elif 255 < len(value) or len(value) < 1:
            raise HTTPException(status_code=422,
                                detail={"error": "type must be between 1 and 255"})
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
            'regular': self.regular,
            'special': self.special,
            'storages': [storage.get() for storage in self.storages]
        }


class CustomerTypeModel(BaseModel):
    B2B: CustomerTypes
    B2C: CustomerTypes
    B2G: CustomerTypes
