from typing import Optional, Any

from pydantic import BaseModel, validator, Field

VALID_INPUT_TYPE = ['Text Field', 'Text Area', 'Text Editor', 'Date', 'Date and Time', 'Yes or No',
                    'Multiple Select', 'Dropdown', 'Price', 'Media Image', 'Color', 'Number']


class Attribute(BaseModel):
    name: str
    label: str
    input_type: int = Field(..., alias='inputType')
    is_required: bool = Field(False, alias='isRequired')
    ecommerce_use_in_filter: bool = Field(False, alias='ecommerceUseInFilter')
    portal_use_in_filter: bool = Field(False, alias='portalUseInFilter')
    portal_use_in_search: bool = Field(False, alias='portalUseInSearch')
    ecommerce_use_in_search: bool = Field(False, alias='ecommerceUseInSearch')
    show_in_portal: bool = Field(True, alias='showInPortal')
    show_in_ecommerce: bool = Field(True, alias='showInEcommerce')
    editable_in_portal: bool = Field(True, alias='editableInPortal')
    editable_in_ecommerce: bool = Field(True, alias='editableInEcommerce')
    regex_pattern: Optional[str] = Field(None, alias='regexPattern')
    parent: str
    default_value: Optional[Any] = Field(None, alias='defaultValue')
    values: Optional[list] = None
    set_to_nodes: bool = Field(False, alias='setToNodes')

    class Config:
        schema_extra = {
            "example": {
                "name": "color-pd",
                "label": "رنگ",
                "inputType": 10,
                "isRequired": False,
                "ecommerceUseInFilter": False,
                "portalUseInFilter": False,
                "portalUseInSearch": False,
                "ecommerceUseInSearch": False,
                "showInPortal": True,
                "showInEcommerce": True,
                "editableInPortal": True,
                "editableInEcommerce": True,
                "regexPattern": "^[a-zA-Z0-9]*$",
                "parent": "100101",
                "defaultValue": "white",
                "values": [{
                    "value": "white",
                    "label": "سفید"
                },
                    {
                        "value": "black",
                        "label": "سیاه"
                    },
                    {
                        "value": "red",
                        "label": "قرمز"
                    },
                    {
                        "value": "green",
                        "label": "سبز"
                    },
                    {
                        "value": "blue",
                        "label": "آبی"
                    }
                ],
                "setToNodes": False
            }
        }

    @validator('default_value')
    def default_value_validator(cls, value):
        if value is None:
            return None
        elif (isinstance(value, int) or isinstance(value, float)) and len(str(value)) > 20:
            raise ValueError('number values must be under 20 character')
        elif isinstance(value, list) or isinstance(value, dict) or isinstance(value, tuple):
            raise ValueError('value must be character, number or boolean')
        elif isinstance(value, str) and (3 > len(value) or len(value) > 256):
            raise ValueError('default value must be between 3 and 256 characters')
        else:
            return value

    @validator('name')
    def name_validator(cls, value):
        if not isinstance(value, str):
            raise ValueError('name must be a string')
        elif 3 > len(value) or len(value) > 256:
            raise ValueError('name must be between 3 and 256 characters')
        return value

    @validator('label')
    def label_validator(cls, value):
        if not isinstance(value, str):
            raise ValueError('label must be a string')
        elif 3 > len(value) or len(value) > 256:
            raise ValueError('label must be between 3 and 256 characters')
        return value

    @validator('input_type')
    def input_type_validator(cls, value):
        if not isinstance(value, int):
            raise ValueError('input_type must be an integer')
        elif -1 >= value or value >= len(VALID_INPUT_TYPE):
            raise ValueError(f'input_type should be between 0 and {len(VALID_INPUT_TYPE) - 1}')
        return VALID_INPUT_TYPE[value]

    @validator('is_required')
    def is_required_validator(cls, value):
        if not isinstance(value, bool):
            raise ValueError('is_required must be a bool')
        return value

    @validator('ecommerce_use_in_filter')
    def ecommerce_use_in_filter_validator(cls, value):
        if not isinstance(value, bool):
            raise ValueError('ecommerce_use_in_filter must be a bool')
        return value

    @validator('portal_use_in_filter')
    def portal_use_in_filter_validator(cls, value):
        if not isinstance(value, bool):
            raise ValueError('portal_use_in_filter must be a bool')
        return value

    @validator('portal_use_in_search')
    def portal_use_in_search_validator(cls, value):
        if not isinstance(value, bool):
            raise ValueError('portal_use_in_search must be a bool')
        return value

    @validator('ecommerce_use_in_search')
    def ecommerce_use_in_search_validator(cls, value):
        if not isinstance(value, bool):
            raise ValueError('ecommerce_use_in_search must be a bool')
        return value

    @validator('show_in_portal')
    def show_in_portal_validator(cls, value):
        if not isinstance(value, bool):
            raise ValueError('show_in_portal must be a bool')
        return value

    @validator('show_in_ecommerce')
    def show_in_ecommerce_validator(cls, value):
        if not isinstance(value, bool):
            raise ValueError('show_in_ecommerce must be a bool')
        return value

    @validator('editable_in_portal')
    def editable_in_portal_validator(cls, value):
        if not isinstance(value, bool):
            raise ValueError('editable_in_portal must be a bool')
        return value

    @validator('editable_in_ecommerce')
    def editable_in_ecommerce_validator(cls, value):
        if not isinstance(value, bool):
            raise ValueError('editable_in_ecommerce must be a bool')
        return value

    @validator('regex_pattern')
    def regex_pattern_validator(cls, value):
        if not isinstance(value, str):
            raise ValueError('regex must be a string')
        elif 3 > len(value) or len(value) > 256:
            raise ValueError('regex_pattern must be between 3 and 256 characters')
        return value

    @validator('parent')
    def parent_validator(cls, value):
        if not isinstance(value, str):
            raise ValueError('parent must be a string')
        elif 3 > len(value) or len(value) > 256:
            raise ValueError('parent must be between 3 and 255 characters')
        return value

    @validator('values')
    def values_validator(cls, value):
        if value is None:
            return value
        if not isinstance(value, list):
            raise ValueError('values must be a list')
        elif len(value) > 128:
            raise ValueError('values must be between 0 and 128 items')
        for item in value:
            if not isinstance(item, dict):
                raise ValueError('values must be a list of dictionaries')
        return value

    @validator('set_to_nodes')
    def set_to_nodes_validator(cls, value):
        if not isinstance(value, bool):
            raise ValueError('set_to_nodes must be a bool')
        return value
