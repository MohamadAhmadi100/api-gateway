from pydantic import BaseModel


class ForceUpdate(BaseModel):
    build_number: int
    build_name: str
    os_type: str
    force_update: bool
    link_download: str

    class Config:
        schema_extra = {
            "example": {
                "build_number": 1,
                "build_name": "1.0.0",
                "os_type": "android",
                "force_update": True,
                "link_download": "https://google.com"
            }
        }
