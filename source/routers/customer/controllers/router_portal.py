import json

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
        value: validation_portal.StaffAuth,
        auth_header=Depends(auth_handler.check_current_user_tokens)
):
    username, token_dict = auth_header
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
