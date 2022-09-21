import re
from enum import Enum
from fastapi import HTTPException
from pydantic import BaseModel, validator, Field
import codemelli


class SellerStatus(str, Enum):
    importer = "importer"
    distributor = "distributor"


class ShipmentMethod(str, Enum):
    aasood = "aasood"
    seller = "seller"


class ProductWarehouse(str, Enum):
    aasood = "aasood"
    seller = "seller"


class PaymentMethod(str, Enum):
    direct = "direct"
    settlement = "settlement"


class Form(BaseModel):
    first_name: str = Field(..., alias="firstName"),
    last_name: str = Field(..., alias="lastName"),
    mobile_number: str = Field(..., alias="mobileNumber"),
    address: str = Field(..., alias="address"),
    seller_status: SellerStatus = Field(..., alias="sellerStatus"),
    shipment_method: ShipmentMethod = Field(..., alias="shipmentMethod"),
    product_warehouse: ProductWarehouse = Field(..., alias="productWarehouse"),
    payment_method: PaymentMethod = Field(..., alias="paymentMethod"),
    national_id: str = Field(..., alias="nationalId")

    @validator("national_id")
    def validate_seller_national_id(cls, national_id):
        pattern = r"^[0-9]{10}$"
        match = re.fullmatch(pattern, national_id)
        if not match:
            raise HTTPException(status_code=422, detail={"error": "کد ملی وارد شده صحیح نمیباشد"})
        if not codemelli.validator(national_id):
            raise HTTPException(status_code=422, detail={"error": "کد ملی وارد شده صحیح نمی باشد"})
        return national_id

    @validator("first_name")
    def validate_seller_first_name(cls, first_name):
        pattern = r"^[\u0600-\u06FF ]{2,32}$"
        match = re.fullmatch(pattern, first_name)
        if not match:
            raise HTTPException(status_code=422, detail={"error": "نام وارد شده صحیح نمیباشد"})
        return first_name

    @validator("last_name")
    def validate_seller_last_name(cls, last_name):
        pattern = r"^[\u0600-\u06FF ]{2,32}$"
        match = re.fullmatch(pattern, last_name)
        if not match:
            raise HTTPException(status_code=422, detail={"error": "نام خانوادگی وارد شده صحیح نمیباشد"})
        return last_name

    @validator("mobile_number")
    def validate_seller_telephone_number(cls, mobile_number):
        pattern = r"^0[0-9]{10}$"
        match = re.fullmatch(pattern, mobile_number)
        if not match:
            raise HTTPException(status_code=422, detail={"message": "لطفا تلفن ثابت خود را به درستی وارد کنید"})
        return mobile_number
