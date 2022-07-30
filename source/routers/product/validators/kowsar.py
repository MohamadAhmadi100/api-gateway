from typing import Optional

from pydantic import BaseModel, Field, validator


class KowsarGroup(BaseModel):
    system_code: str = Field(..., alias="systemCode")
    name: str = Field(..., alias="name")
    configs: Optional[dict] = Field(None)
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

    @validator('configs')
    def check_configs(cls, v):
        if not isinstance(v, dict):
            raise ValueError('configs must be an instance of dict')
        return v

    class Config:
        schema_extra = {
            "example": {
                "systemCode": "12345",
                "name": "Kowsar",
                "parentSystemCode": "12345",
                "configs": {
                    "storage": "32GB",
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


class KowsarPart(BaseModel):
    """
    Kowsar model
    """
    system_code: str = Field(..., alias="systemCode")
    storage_ids: list = Field(..., alias="storageIds")
    parent_system_code: str = Field(..., alias="parentSystemCode")
    guaranty: str = Field(..., alias="guaranty")

    @validator("system_code")
    def check_model_code(cls, v):
        if not isinstance(v, str):
            raise ValueError('system_code must be an instance of str')
        return v

    @validator("storage_ids")
    def check_storage_ids(cls, v):
        if not isinstance(v, list):
            raise ValueError('storage_ids must be an instance of list')
        return v

    @validator("parent_system_code")
    def check_parent_system_code(cls, v):
        if not isinstance(v, str):
            raise ValueError('parent_system_code must be an instance of str')
        return v

    @validator("guaranty")
    def check_guaranty(cls, v):
        if not isinstance(v, str):
            raise ValueError('guaranty must be an instance of str')
        return v

    class Config:
        schema_extra = {
            "example": {
                "systemCode": "12345",
                "storageIds": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"],
                "parentSystemCode": "12345",
                "guaranty": "Awat"
            }
        }


class KowsarConfig(BaseModel):
    config_type: str = Field(..., alias="configType")
    system_code: str = Field(..., alias="systemCode")
    name: str = Field(..., alias="name")

    @validator('config_type')
    def check_config_type(cls, v):
        if not isinstance(v, str):
            raise ValueError('config_type must be an instance of str')
        return v

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
