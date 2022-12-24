from typing import List, Union, Optional

from pydantic import BaseModel, Field


class Attribute(BaseModel):
    name: str
    ecommerce_use_in_filter: bool
    ecommerce_use_in_search: bool
    editable_in_ecommerce: bool
    editable_in_portal: bool
    label: str
    portal_use_in_filter: bool
    portal_use_in_search: bool
    show_in_ecommerce: bool
    show_in_portal: bool
    value: Optional[str] = None


class Product(BaseModel):
    systemCode: str = Field(alias="systemCode")
    storageId: str = Field(alias="storageId")
    price: int
    count: int
    model: str
    name: str
    brand: dict
    color: dict
    guarantee: dict
    seller: dict
    mainCategory: dict = Field(alias="mainCategory")
    subCategory: dict = Field(alias="subCategory")
    attributes: Union[List[Attribute], list]



class RequestGoods(BaseModel):
    products: Union[List[Product], list] = Field(alias="products")
    shipment: dict = Field(alias="shipment")
    storage_id: str = Field(alias="storageId")


class SubmitRequestForms(BaseModel):
    referral_number: str = Field(alias="referralNumber")
    customer_id: str = Field(alias="customerId")
    details: RequestGoods


p = {
    "products": [{
        "systemCode": "2000010010001001001001001",
        "storageId": "1",
        "brand": {
            "value": "Samsung",
            "label": "Samsung"
        },
        "model": "A01 Core",
        "name": "Mobile Samsung A01 Core (1GB 16GB 4G) Vietnam",
        "color": {
            "value": "white",
            "label": "white"
        },
        "guarantee": {
            "value": "Aawaat",
            "label": "Aawaat"
        },
        "seller": {
            "value": "ASD",
            "label": "ASD"
        },
        "price": 618000,
        "count": 1,
        "mainCategory": {
            "value": "Device",
            "label": "Device"
        },
        "subCategory": {
            "value": "Mobile",
            "label": "Mobile"
        },
        "attributes": [
            {
                "name": "simnum-pd",
                "ecommerce_use_in_filter": False,
                "ecommerce_use_in_search": False,
                "editable_in_ecommerce": True,
                "editable_in_portal": True,
                "label": "سیم کارت",
                "portal_use_in_filter": False,
                "portal_use_in_search": False,
                "show_in_ecommerce": True,
                "show_in_portal": True,
                "value": None
            }
        ]
    }],
    "shipment": {},
    "storageId": "1"
}




# attr = [
#             {
#                 "name": "simnum-pd",
#                 "ecommerce_use_in_filter": false,
#                 "ecommerce_use_in_search": false,
#                 "editable_in_ecommerce": true,
#                 "editable_in_portal": true,
#                 "label": "سیم کارت",
#                 "portal_use_in_filter": false,
#                 "portal_use_in_search": false,
#                 "show_in_ecommerce": true,
#                 "show_in_portal": true,
#                 "value": None
#             },
#             {
#                 "name": "description-pd",
#                 "ecommerce_use_in_filter": false,
#                 "ecommerce_use_in_search": false,
#                 "editable_in_ecommerce": true,
#                 "editable_in_portal": true,
#                 "label": "توضیحات",
#                 "portal_use_in_filter": false,
#                 "portal_use_in_search": false,
#                 "show_in_ecommerce": true,
#                 "show_in_portal": true,
#                 "value": None
#             },
#             {
#                 "name": "charger-pd",
#                 "ecommerce_use_in_filter": false,
#                 "ecommerce_use_in_search": false,
#                 "editable_in_ecommerce": true,
#                 "editable_in_portal": true,
#                 "label": "شارژر",
#                 "portal_use_in_filter": false,
#                 "portal_use_in_search": false,
#                 "show_in_ecommerce": true,
#                 "show_in_portal": true,
#                 "value": None
#             },
#             {
#                 "name": "handsfree-pd",
#                 "ecommerce_use_in_filter": false,
#                 "ecommerce_use_in_search": false,
#                 "editable_in_ecommerce": true,
#                 "editable_in_portal": true,
#                 "label": "هندزفری",
#                 "portal_use_in_filter": false,
#                 "portal_use_in_search": false,
#                 "show_in_ecommerce": true,
#                 "show_in_portal": true,
#                 "value": None
#             },
#             {
#                 "name":True,
#                 "ecommerce_use_in_filter": false,
#                 "ecommerce_use_in_search": false,
#                 "editable_in_ecommerce": true,
#                 "editable_in_portal": true,
#                 "label": "گلس",
#                 "portal_use_in_filter": false,
#                 "portal_use_in_search": false,
#                 "show_in_ecommerce": true,
#                 "show_in_portal": true,
#                 "value": None
#             },
#             {
#                 "name": "case-pd",
#                 "ecommerce_use_in_filter": false,
#                 "ecommerce_use_in_search": false,
#                 "editable_in_ecommerce": true,
#                 "editable_in_portal": true,
#                 "label": "قاب",
#                 "portal_use_in_filter": false,
#                 "portal_use_in_search": false,
#                 "show_in_ecommerce": true,
#                 "show_in_portal": true,
#                 "value": None
#             },
#             {
#                 "name": "weight-pd",
#                 "ecommerce_use_in_filter": false,
#                 "ecommerce_use_in_search": false,
#                 "editable_in_ecommerce": true,
#                 "editable_in_portal": true,
#                 "label": "وزن",
#                 "portal_use_in_filter": false,
#                 "portal_use_in_search": false,
#                 "show_in_ecommerce": true,
#                 "show_in_portal": true,
#                 "value": None
#             },
#             {
#                 "name": "screen-pd",
#                 "ecommerce_use_in_filter": false,
#                 "ecommerce_use_in_search": false,
#                 "editable_in_ecommerce": true,
#                 "editable_in_portal": true,
#                 "label": "صفحه نمایش",
#                 "portal_use_in_filter": false,
#                 "portal_use_in_search": false,
#                 "show_in_ecommerce": true,
#                 "show_in_portal": true,
#                 "value": None
#             },
#             {
#                 "name": "storage-pd",
#                 "ecommerce_use_in_filter": false,
#                 "ecommerce_use_in_search": false,
#                 "editable_in_ecommerce": true,
#                 "editable_in_portal": true,
#                 "label": "حافظه",
#                 "portal_use_in_filter": false,
#                 "portal_use_in_search": false,
#                 "show_in_ecommerce": true,
#                 "show_in_portal": true,
#                 "value": None
#             },
#             {
#                 "name": "fa-support-pd",
#                 "ecommerce_use_in_filter": false,
#                 "ecommerce_use_in_search": false,
#                 "editable_in_ecommerce": true,
#                 "editable_in_portal": true,
#                 "label": "پشتیبانی از زبان فارسی",
#                 "portal_use_in_filter": false,
#                 "portal_use_in_search": false,
#                 "show_in_ecommerce": true,
#                 "show_in_portal": true,
#                 "value": None
#             },
#             {
#                 "name": "communication-networks-pd",
#                 "ecommerce_use_in_filter": false,
#                 "ecommerce_use_in_search": false,
#                 "editable_in_ecommerce": true,
#                 "editable_in_portal": true,
#                 "label": "شبکه های ارتباطی",
#                 "portal_use_in_filter": false,
#                 "portal_use_in_search": false,
#                 "show_in_ecommerce": true,
#                 "show_in_portal": true,
#                 "value": None
#             },
#             {
#                 "name": "mainImage-pd",
#                 "ecommerce_use_in_filter": false,
#                 "ecommerce_use_in_search": false,
#                 "editable_in_ecommerce": true,
#                 "editable_in_portal": true,
#                 "label": "تصویر اصلی",
#                 "portal_use_in_filter": false,
#                 "portal_use_in_search": false,
#                 "show_in_ecommerce": true,
#                 "show_in_portal": true,
#                 "value": "https://devapi.aasood.com/gallery_files/product/100103008001/mainImage-pd/500x400.jpg"
#             },
#             {
#                 "name": "otherImage-pd",
#                 "ecommerce_use_in_filter": false,
#                 "ecommerce_use_in_search": false,
#                 "editable_in_ecommerce": true,
#                 "editable_in_portal": true,
#                 "label": "تصاویر دیگر",
#                 "portal_use_in_filter": false,
#                 "portal_use_in_search": false,
#                 "show_in_ecommerce": true,
#                 "show_in_portal": true,
#                 "value": None
#             },
#             {
#                 "name": "closeImage-pd",
#                 "ecommerce_use_in_filter": false,
#                 "ecommerce_use_in_search": false,
#                 "editable_in_ecommerce": true,
#                 "editable_in_portal": true,
#                 "label": "نمای نزدیک",
#                 "portal_use_in_filter": false,
#                 "portal_use_in_search": false,
#                 "show_in_ecommerce": true,
#                 "show_in_portal": true,
#                 "value": None
#             }
#         ]