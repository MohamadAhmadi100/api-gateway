import json
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, Body
from fastapi import Response

# from customer.models.model_register import Customer
# from customer.modules import log
from source.message_broker.rabbit_server import RabbitRPC
from source.routers.customer.module.auth import AuthHandler
from source.routers.customer.validators import validation_register

router_register = APIRouter(
    prefix="/register",
    tags=["register"]
)

rpc = RabbitRPC(exchange_name='headers_exchange', timeout=5)
rpc.connect()
rpc.consume()

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
    rpc.response_len_setter(response_len=1)
    result = rpc.publish(
        message={
            "customer": {
                "action": "register",
                "body": {
                    "values": value.dict()

                }
            }
        },
        headers={'customer': True}
    )
    customer_result = result.get("customer", {})
    if not customer_result.get("success"):
        raise HTTPException(
            status_code=customer_result.get("status_code", 500),
            detail={"error": customer_result.get("error", "Something went wrong")}
        )
    else:
        customer_info = customer_result.get("message").get('data')
        sub_dict = {
            "user_id": customer_info.get('customerID'),
            "customer_type": customer_info.get('customerType'),
            "phone_number": customer_info.get('customerPhoneNumber'),
        }
        response.headers["refreshToken"] = auth_handler.encode_refresh_token(sub_dict)
        response.headers["accessToken"] = auth_handler.encode_access_token(sub_dict)
        response.status_code = customer_result.get("status_code", 200)
        return customer_result
