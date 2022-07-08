import re
from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel, Field, validator
from pydantic.main import create_model


class CreateClass:
    __slots__ = [
        "__class",
        "_class_name",
        "_class_parent",
        "_attributes_dict",
        "_class_attributes_dict",
        "_class_validator_dict",
        "_key",
    ]

    def __init__(
            self,
            class_name: str,
            attributes: dict,
            parent: Optional[object] = BaseModel
    ):
        self.__class: object = None
        self._class_parent: object = parent
        self._class_name: str = class_name
        self._attributes_dict: dict = attributes
        self._class_attributes_dict: dict = {}
        self._class_validator_dict: dict = {}
        self._key = None

    def make_class_attributes(self) -> None:
        for key, value in self._attributes_dict.items():
            self._class_attributes_dict[key] = Field(**value)
            value_type = str
            if value.get('input_type') == "Yes or No":
                value_type = bool
            elif value.get('input_type') == "Multiple Select":
                value_type = list
            elif value.get('input_type') == "Price":
                value_type = int
            elif value.get('input_type') == "Number":
                value_type = int
            if value.get("required") or value.get("is_required") or value.get("isRequired"):
                self._class_attributes_dict[key] = (value_type, Field(**value))
            else:
                self._class_attributes_dict[key] = (Optional[value_type], Field(**value))

    def make_validator_dict(self):
        for key, value in self._class_attributes_dict.items():
            self._key = key
            self._class_validator_dict[f'{key}_validate'] = validator(key, allow_reuse=True)(
                self.make_validator_function)

    def make_validator_function(self, value: any) -> any:
        value_type = self._attributes_dict.get(self._key, {}).get("type")
        regex_pattern = self._attributes_dict.get(self._key, {}).get("regex_pattern")
        max_length = self._attributes_dict.get(self._key, {}).get("maxLength")
        min_length = self._attributes_dict.get(self._key, {}).get("minLength")
        if regex_pattern:
            match = re.fullmatch(regex_pattern, value)
            if not match:
                raise HTTPException(status_code=422, detail={"error": f" صحیح نمیباشد {value} الگوی "})

        if value_type and not isinstance(value, value_type):
            raise HTTPException(status_code=422, detail={"error": f" صحیح نمیباشد {value} نوع داده "})

        if max_length and max_length < len(value):
            raise HTTPException(status_code=422, detail={"error": f"  باشد {value} طول داده باید کمتر از "})

        if min_length and min_length > len(value):
            raise HTTPException(status_code=422, detail={"error": f"  باشد {value} طول داده باید بیشتر از "})

        return value

    def make_class(self) -> None:
        self.__class: object = create_model(
            self._class_name,
            __base__=self._class_parent,
            **self._class_attributes_dict,
            **self._class_validator_dict,
        )

    def get_pydantic_class(self) -> object:
        self.make_class_attributes()
        self.make_validator_dict()
        self.make_class()
        return self.__class
