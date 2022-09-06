import logging

import codemelli
from fastapi import APIRouter, HTTPException, Response
from unidecode import unidecode
# import source.services.address.address_router as address_funcs
# import source.services.customer.router_register as register_funcs
from source.helpers.exception_handler import LogHandler
# from source.helpers.rabbit_config import new_rpc
from source.routers.customer.module.auth import AuthHandler
from source.routers.customer.validators import validation_register
from source.message_broker.rabbit_server import RabbitRPC

router_register = APIRouter(
    prefix="/register",
    tags=["register"]
)

auth_handler = AuthHandler()


@router_register.get("/")
def register_validation_generator():
    form = validation_register.CustomerRegister.schema().get("properties").copy()
    return {"fields": form}


@router_register.post("/")
def register(
        response: Response,
        value: validation_register.CustomerRegister,
):
    try:
        # nationalCode = unidecode(f"u{value.customer_national_id}")
        if not codemelli.validator(value.customer_national_id):
            raise HTTPException(status_code=422, detail={"error": "کد ملی وارد شده صحیح نمی باشد"})
    except Exception as e:
        raise HTTPException(status_code=422, detail={"error": "کد ملی وارد شده صحیح نمی باشد"}) from e
    try:
        customer_phone_number = unidecode(value.customer_phone_number)
        customer_national_id = unidecode(value.customer_national_id)
        customer_postal_code = unidecode(value.customer_postal_code)
        customer_tel = unidecode(value.customer_telephone)
    except Exception as exc:
        raise HTTPException(status_code=422, detail={"error": "لطفا مقادیر عددی را به درستی وارد کنید"}) from exc

    address = {
        "customer_name": f"{value.customer_first_name} {value.customer_last_name}",
        "state_name": value.customer_address_province,
        "state_id": value.customer_address_province_id,
        "city_id": value.customer_address_city_id,
        "city_name": value.customer_address_city,
        "region_code": value.customer_region_code,
        "street": value.customer_street,
        "alley": value.customer_alley,
        "plaque": value.customer_plaque,
        "unit": value.customer_unit,
        "tel": customer_tel,
        "postal_code": customer_postal_code,
        "is_default": True
    }
    customer_address = {
        "customer_name": f"{value.customer_first_name} {value.customer_last_name}",
        "state_name": value.customer_province,
        "state_id": value.customer_province_id,
        "city_id": value.customer_city_id,
        "city_name": value.customer_city,
        "region_code": value.customer_region_code,
        "street": value.customer_street,
        "alley": value.customer_alley,
        "plaque": value.customer_plaque,
        "unit": value.customer_unit,
        "tel": customer_tel,
        "postal_code": customer_postal_code,
        "fullAddress": f"{value.customer_address_province}, {value.customer_address_city}, {value.customer_street}, {value.customer_alley}, پلاک: {value.customer_plaque}, ,واحد: {value.customer_unit}"
    }

    customer_type = [value.customer_type] if value.customer_type else ["B2B"]
    data = {
        "customer_phone_number": customer_phone_number,
        "customer_first_name": value.customer_first_name,
        "customer_last_name": value.customer_last_name,
        "customer_national_id": customer_national_id,
        "customer_password": value.customer_password,
        "customer_verify_password": value.customer_verify_password,
        "customer_address": [customer_address],
        "customer_document_status": value.customer_document_status,
        "customer_region_code": value.customer_region_code,
        "customer_city_name": value.customer_city,
        "customer_city_id": value.customer_city_id,
        "customer_state_name": value.customer_province,
        "customer_state_id": value.customer_province_id,
        "customer_ofogh_code": value.customer_ofogh_code,
        "customer_postal_code": customer_postal_code,
        "customer_type": customer_type
    }
    # customer_result = new_rpc.publish(
    #     message=[
    #         register_funcs.register(data=data)]
    # )
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        customer_result = rpc.publish(
            message={
                "customer": {
                    "action": "register",
                    "body": {
                        "data": data
                    }
                }
            },
            headers={'customer': True}
        ).get("customer", {})
    if not customer_result.get("success"):
        raise HTTPException(
            status_code=customer_result.get("status_code", 500),
            detail={"error": customer_result.get("error", "Something went wrong")}
        )
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            LogHandler("log/app.log", mode='a',
                       maxBytes=5_000_000,
                       backupCount=8),
        ]
    )
    customer_id = customer_result.get("message").get("data").get("customerID")
    # address_result = new_rpc.publish(
    #     message=[
    #         address_funcs.insert_address(data=address, customerId=str(customer_id))]
    # )
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        address_result = rpc.publish(
            message={
                "address": {
                    "action": "insert_address",
                    "body": {
                        "data": address,
                        "customerId": str(customer_id)
                    }
                }
            },
            headers={'address': True}
        ).get("address", {})
    if not address_result.get("success"):
        raise HTTPException(
            status_code=317,
            detail={"message": "برای ثبت آدرس دوباره تلاش کنید"}
        )
    response.status_code = customer_result.get("status_code", 200)
    return customer_result.get("message")
