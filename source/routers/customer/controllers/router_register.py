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
    print(value.dict())
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
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
    response.status_code = customer_result.get("status_code", 200)
    return customer_result.get("message")
