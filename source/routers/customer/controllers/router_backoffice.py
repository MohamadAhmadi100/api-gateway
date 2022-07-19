from fastapi import Response, Depends, HTTPException
from fastapi import APIRouter
# from source.message_broker.rabbit_server import RabbitRPC
from source.routers.customer.module.auth import AuthHandler
from source.routers.customer.validators import validation_portal
from source.helpers.rabbit_config import new_rpc

router_portal = APIRouter(
    prefix="/portal",
    tags=["portal"]
)

auth_handler = AuthHandler()


@router_portal.post("/")
def get_customers_data(
        response: Response,
        value: validation_portal.StaffAuth = None,
        auth_header=Depends(auth_handler.check_current_user_tokens)
):
    username, token_dict = auth_header
    # with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
    #     rpc.response_len_setter(response_len=1)
    result = new_rpc.publish(
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
        # auth_header=Depends(auth_handler.check_current_user_tokens)
):
    # username, token_dict = auth_header
    # with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
    #     rpc.response_len_setter(response_len=1)
    if value:
        result = new_rpc.publish(
            message={
                "customer": {
                    "action": "get_customers_grid_data",
                    "body": {
                        "data": value.json()
                    }
                }
            },
            headers={'customer': True}
        )
    else:
        result = new_rpc.publish(
            message={
                "customer": {
                    "action": "get_customers_grid_data",
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


@router_portal.put("/")
def get_customers_data(
        response: Response,
        value: validation_portal.StaffAuth = None,
        auth_header=Depends(auth_handler.check_current_user_tokens)
):
    username, token_dict = auth_header
    # with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
    #     rpc.response_len_setter(response_len=1)
    if value:
        result = new_rpc.publish(
            message={
                "customer": {
                    "action": "get_customers_grid_data",
                    "body": {
                        "data": value.json()
                    }
                }
            },
            headers={'customer': True}
        )
    else:
        result = new_rpc.publish(
            message={
                "customer": {
                    "action": "get_customers_grid_data",
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
