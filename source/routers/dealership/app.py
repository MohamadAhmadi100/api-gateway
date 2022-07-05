from fastapi import FastAPI, HTTPException, Response, responses, Depends
from source.config import settings
from starlette.exceptions import HTTPException as starletteHTTPException
from source.message_broker.rabbit_server import RabbitRPC
from source.routers.address.validators.address import Address, AddressId
from source.routers.address.validators.update_address import UpdateAddress
from source.routers.customer.module.auth import AuthHandler
from source.routers.dealership.validators.dealership import RequestGoods

TAGS = [
    {
        "name": "Dealership",
        "description": "Dealership application endpoints"
    }
]
app = FastAPI(
    title="Dealership API service",
    description="This is Dealership gateway MicroService",
    version="0.1.0",
    openapi_tags=TAGS,
    docs_url="/docs/",
    redoc_url="/redoc/",
    debug=settings.DEBUG_MODE
)

auth_handler = AuthHandler()


@app.post("/create_request_goods", tags=["request for goods from dealership"])
def create_request(data: RequestGoods,
                   response: Response,
                   auth_header=Depends(auth_handler.check_current_user_tokens)):
    user, token = auth_header
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        dealership_response = rpc.publish(
            message={
                "dealership": {
                    "action": "insert_goods_request",
                    "body": {
                        "data": dict(data),
                        "credit": 10000000,
                        "customer_id": str(user.get("user_id"))
                    }
                }
            },
            headers={'address': True}
        ).get("address", {})

        if dealership_response.get("success"):
            return dealership_response
        raise HTTPException(status_code=dealership_response.get("status_code", 500),
                            detail={"error": dealership_response.get("error", "Dealership service Internal error")})