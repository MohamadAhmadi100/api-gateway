from fastapi import HTTPException
from pydantic import BaseModel, validator


class Cart(BaseModel):
    count: int
    storage_id: str
    price: int
    user_info: dict
    products: dict

    @validator("storage_id")
    def stock_id_validator(cls, value):
        if not isinstance(value, str):
            raise HTTPException(status_code=422, detail={"error": "storage_id must be str"})
        return value

    @validator("count")
    def count_validator(cls, value):
        if not isinstance(value, int):
            raise HTTPException(status_code=422, detail={"error": "count must be int"})
        elif 0 > value:
            raise HTTPException(status_code=422, detail={"error": "count cant be less than 0"})
        return value

    @validator("price")
    def price_validator(cls, value):
        if not isinstance(value, int):
            raise HTTPException(status_code=422, detail={"error": "price must be int"})
        return value

    @validator("user_info")
    def user_info_validator(cls, value):
        if not isinstance(value, dict):
            raise HTTPException(status_code=422, detail={"error": "user_info must be dict"})
        elif 'user_id' not in value.keys():
            raise HTTPException(status_code=422, detail={"error": "user_id must be a key of user_info"})
        return value

    @validator("products")
    def product_validator(cls, value):
        if not isinstance(value, dict):
            raise HTTPException(status_code=422, detail={"error": "products must be int"})
        elif 'system_code' not in value.keys():
            raise HTTPException(status_code=422, detail={"error": "system_code must be a key of products"})
        return value

    class Config:
        schema_extra = {
            "example": {
                "user_info": {
                    "user_id": 0
                },
                'products': {
                    "system_code": "111"
                },
                "count": 1,
                "storage_id": '1',
                "price": 0

            }
        }
