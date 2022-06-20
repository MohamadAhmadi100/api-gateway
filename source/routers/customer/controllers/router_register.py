from fastapi import APIRouter, HTTPException, Response
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
    customer_id = customer_result.get("data").get("customerID")
    if not customer_result.get("success"):
        raise HTTPException(
            status_code=customer_result.get("status_code", 500),
            detail={"error": customer_result.get("error", "Something went wrong")}
        )
    print(value.dict)
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        address_response = rpc.publish(
            message={
                "address": {
                    "action": "insert_address",
                    "body": {
                        "data": value.dict,
                        "customerId": str(customer_id)
                    }
                }
            },
            headers={'address': True}
        ).get("address", {})
        if not address_response.get("success"):
            raise HTTPException(
                status_code=317,
                detail={"message": "برای ثبت آدرس دوباره تلاش کنید"}
            )
    response.status_code = customer_result.get("status_code", 200)
    return customer_result.get("message")
