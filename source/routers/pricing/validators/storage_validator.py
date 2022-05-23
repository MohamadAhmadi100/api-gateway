from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel, validator, Field


class StoragesModel(BaseModel):
    storage_id: str = Field(..., alias="storageId")
    regular: int
    informal: Optional[int] = None
    special: Optional[int] = None
    special_from_date: Optional[str] = Field(..., alias='specialFromDate')
    special_to_date: Optional[str] = Field(..., alias='specialToDate')

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

    @validator('informal')
    def informal_validator(cls, value):
        if not isinstance(value, int):
            raise HTTPException(status_code=422, detail={"error": "informal must be int"})
        elif 100_000_000_000_000 < value or value < 1:
            raise HTTPException(status_code=422, detail={"error": "informal must be between 1 and 100_000_000_000_000"})
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
