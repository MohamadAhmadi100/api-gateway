from fastapi import APIRouter, HTTPException
from fastapi import Response

# from customer.models.model_register import Customer
# from customer.mudoles import log
from source.message_broker.rabbit_server import RabbitRPC
from source.routers.customer.models.auth import AuthHandler
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
    cart_result = result.get("customer", {})
    if not cart_result.get("success"):
        raise HTTPException(status_code=cart_result.get("status_code", 500),
                            detail={"error": cart_result.get("error", "Something went wrong")})
    else:
        response.headers["refreshToken"] = auth_handler.encode_refresh_token(user_id=value.customer_phone_number)
        response.headers["accessToken"] = auth_handler.encode_access_token(user_id=value.customer_phone_number)
        response.status_code = cart_result.get("status_code", 200)
        return cart_result.get("message")
