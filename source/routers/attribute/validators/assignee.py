from pydantic import BaseModel, validator


class Assignee(BaseModel):
    name: str = None

    class Config:
        schema_extra = {
            "example": {
                "name": "product"
            }
        }

    @validator('name')
    def assignee_validator(cls, value):
        if value is None:
            raise ValueError('name is required')
        elif not isinstance(value, str):
            raise ValueError('name must be a string')
        elif 3 > len(value) or len(value) > 128:
            raise ValueError('name must be between 3 and 128 items')
        return value
