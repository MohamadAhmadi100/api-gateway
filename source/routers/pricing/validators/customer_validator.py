from typing import Optional, List

from fastapi import HTTPException
from pydantic import BaseModel, validator, Field

from source.routers.pricing.validators.storage_validator import StoragesModel


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
