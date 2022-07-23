from fastapi import APIRouter, HTTPException, Response
import codemelli
from unidecode import unidecode
# from source.message_broker.rabbit_server import RabbitRPC
from source.routers.customer.module.auth import AuthHandler
from source.routers.customer.validators import validation_register
import logging
from source.helpers.exception_handler import LogHandler
from source.helpers.rabbit_config import new_rpc

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
    address = {
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
        "tel": value.customer_telephone,
        "postal_code": value.customer_postal_code,
        "is_default": True
    }
    customer_address = {
        "customerStateName": value.customer_province,
        "customerStateId": value.customer_province_id,
        "customerCityId": value.customer_city_id,
        "customerCityName": value.customer_city,
        "customerRegionCode": value.customer_region_code,
        "customerStreet": value.customer_street,
        "customerAlley": value.customer_alley,
        "customerPlaque": value.customer_plaque,
        "customerUnit": value.customer_unit,
        "customerTelephone": value.customer_telephone,
        "customerPostalCode": value.customer_postal_code,
        "fullAddress": f"{value.customer_province}, {value.customer_city}, {value.customer_street}, {value.customer_alley}, پلاک: {value.customer_plaque}, ,واحد: {value.customer_unit}"
    }
    # with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
    #     rpc.response_len_setter(response_len=1)
    result = new_rpc.publish(
        message={
            "customer": {
                "action": "register",
                "body": {
                    "data": {
                        "customer_phone_number": value.customer_phone_number,
                        "customer_first_name": value.customer_first_name,
                        "customer_last_name": value.customer_last_name,
                        "customer_national_id": value.customer_national_id,
                        "customer_password": value.customer_password,
                        "customer_verify_password": value.customer_verify_password,
                        "customer_street": value.customer_street,
                        "customer_address": [customer_address],
                        "customer_document_status": value.customer_document_status
                    }
                }
            }
        }
    )
    customer_result = result.get("customer", {})
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
    # with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
    #     rpc.response_len_setter(response_len=1)
    address_response = new_rpc.publish(
        message={
            "address": {
                "action": "insert_address",
                "body": {
                    "data": address,
                    "customerId": str(customer_id)
                }
            }
        }
    ).get("address", {})
    if not address_response.get("success"):
        raise HTTPException(
            status_code=317,
            detail={"message": "برای ثبت آدرس دوباره تلاش کنید"}
        )
    response.status_code = customer_result.get("status_code", 200)
    return customer_result.get("message")
