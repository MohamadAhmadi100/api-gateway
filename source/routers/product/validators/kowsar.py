from typing import Optional

from pydantic import BaseModel, Field, validator


class ProductConfig(BaseModel):
    storage: Optional[str] = Field(None)
    color: Optional[str] = Field(None)
    guarantee: Optional[str] = Field(None)
    ram: Optional[str] = Field(None)
    network: Optional[str] = Field(None)
    capacity: Optional[str] = Field(None)
    sim: Optional[str] = Field(None)
    year: Optional[str] = Field(None)
    type: Optional[str] = Field(None)
    power: Optional[str] = Field(None)
    part_number: Optional[str] = Field(None)
    processor: Optional[str] = Field(None)

    @validator('storage')
    def storage_validator(cls, v):
        if not isinstance(v, str):
            return None
        return v

    @validator('color')
    def color_validator(cls, v):
        if not isinstance(v, str):
            return None
        return v

    @validator('guarantee')
    def guarantee_validator(cls, v):
        if not isinstance(v, str):
            return None
        return v

    @validator('ram')
    def ram_validator(cls, v):
        if not isinstance(v, str):
            return None
        return v

    @validator('network')
    def network_validator(cls, v):
        if not isinstance(v, str):
            return None
        return v

    @validator('capacity')
    def capacity_validator(cls, v):
        if not isinstance(v, str):
            return None
        return v

    @validator('sim')
    def sim_validator(cls, v):
        if not isinstance(v, str):
            return None
        return v

    @validator('year')
    def year_validator(cls, v):
        if not isinstance(v, str):
            return None
        return v

    @validator('type')
    def type_validator(cls, v):
        if not isinstance(v, str):
            return None
        return v

    @validator('power')
    def power_validator(cls, v):
        if not isinstance(v, str):
            return None
        return v

    @validator('part_number')
    def part_number_validator(cls, v):
        if not isinstance(v, str):
            return None
        return v

    @validator('processor')
    def processor_validator(cls, v):
        if not isinstance(v, str):
            return None
        return v


class KowsarPart(BaseModel):
    """
    Kowsar model
    """
    model_code: str = Field(..., alias="modelCode")
    config: ProductConfig = Field(...)
    storage_ids: list = Field(...)

    @validator('config')
    def check_config(cls, v):
        if not isinstance(dict(v), dict):
            raise ValueError('config must be an instance of dict')
        return v

    @validator("model_code")
    def check_model_code(cls, v):
        if not isinstance(v, str):
            raise ValueError('model_code must be an instance of str')
        return v

    @validator("storage_ids")
    def check_storage_ids(cls, v):
        if not isinstance(v, list):
            raise ValueError('storage_ids must be an instance of list')
        return v

    class Config:
        schema_extra = {
            "example": {
                "modelCode": "12345",
                "storage_ids": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"],
                "config": {
                    "storage": "32GB",
                    "color": "black",
                    "guarantee": "12 months",
                    "ram": "4GB",
                    "network": "2G",
                    "capacity": "32GB",
                    "sim": "yes",
                    "year": "2019",
                    "type": "phone",
                    "power": "500W",
                    "part_number": "12345",
                    "processor": "snapdragon"
                }
            }
        }


class KowsarGroup(BaseModel):
    system_code: str = Field(..., alias="systemCode")
    name: str = Field(..., alias="name")
    parent_system_code: str = Field(..., alias="parentSystemCode")

    @validator('system_code')
    def check_system_code(cls, v):
        if not isinstance(v, str):
            raise ValueError('system_code must be an instance of str')
        return v

    @validator('name')
    def check_name(cls, v):
        if not isinstance(v, str):
            raise ValueError('name must be an instance of str')
        return v

    @validator('parent_system_code')
    def check_parent_system_code(cls, v):
        if not isinstance(v, str):
            raise ValueError('parent_system_code must be an instance of str')
        return v

    class Config:
        schema_extra = {
            "example": {
                "systemCode": "12345",
                "name": "Kowsar",
                "parentSystemCode": "12345"
            }
        }
