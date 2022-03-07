"""
working with file types
"""
from typing import List

from pydantic import BaseModel


class Dimensions(BaseModel):
    width: int
    hight: int


class Gallery(BaseModel):
    file_type: str
    is_image: bool
    max_size: int
    formats: List[str]
    dimensions: List[Dimensions]

    def get(self):
        return {
            "file_type": self.file_type,
            "is_image": self.is_image,
            "max_size": self.max_size,
            "formats": self.formats,
            "dimensions": [val.dict() for val in self.dimensions]
        }
