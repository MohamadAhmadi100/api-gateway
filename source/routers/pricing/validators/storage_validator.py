from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel, validator


class StoragesModel(BaseModel):
    storage_id: str
    regular: int
    special: Optional[int] = None

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

    def get(self) -> dict:
        return {
            'storage_id': self.storage_id,
            'regular': self.regular,
            'special': self.special
        }
