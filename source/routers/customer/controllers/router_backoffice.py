import json
from typing import Optional

from fastapi import Response, Depends, HTTPException
from fastapi import status, APIRouter
from source.message_broker.rabbit_server import RabbitRPC
from source.routers.customer.module.auth import AuthHandler
from source.routers.customer.validators import validation_portal

router_portal = APIRouter(
    prefix="/portal",
    tags=["portal"]
)

auth_handler = AuthHandler()

rpc = RabbitRPC(exchange_name='headers_exchange', timeout=5)
rpc.connect()
rpc.consume()


@router_portal.post("/")
def get_customers_data(
        response: Response,
        value: validation_portal.StaffAuth = None,
        auth_header=Depends(auth_handler.check_current_user_tokens)
):
    username, token_dict = auth_header
    print(value)
    rpc.response_len_setter(response_len=1)
    result = rpc.publish(
        message={
            "customer": {
                "action": "get_customers_data",
                "body": {
                }
            }
        },
        headers={'customer': True}
    )
    customer_result = result.get("customer", {})
    response.status_code = customer_result.get("status_code", 200)
    return customer_result.get("message")


@router_portal.post("/raw")
def get_customers_data(
        response: Response,
        value: validation_portal.StaffAuth = None,
        auth_header=Depends(auth_handler.check_current_user_tokens)
):
    username, token_dict = auth_header
    rpc.response_len_setter(response_len=1)
    result = rpc.publish(
        message={
            "customer": {
                "action": "get_customers_grid_data",
                "body": {
                    "data": dict(value)
                }
            }
        },
        headers={'customer': True}
    )
    customer_result = result.get("customer", {})
    customer_result = {}
    if not customer_result.get("success"):
        raise HTTPException(
            status_code=customer_result.get("status_code", 500),
            detail={"error": customer_result.get("error", "Something went wrong")}
        )
    else:
        response.status_code = customer_result.get("status_code", 200)
        print(customer_result)
        return customer_result.get("message")
