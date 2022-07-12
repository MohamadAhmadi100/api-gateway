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
                   auth_header=Depends(auth_handler.check_current_user_tokens)):
    user, token = auth_header
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        check_credit = rpc.publish(
            message={
                "credit": {
                    "action": "check_credit",
                    "body": {}
                }
            },
            headers={'dealership': True}
        ).get("dealership", {})

        if referral_response.get("success"):
        rpc.response_len_setter(response_len=1)
        referral_response = rpc.publish(
            message={
                "dealership": {
                    "action": "get_referral_number",
                    "body": {}
                }
            },
            headers={'dealership': True}
        ).get("dealership", {})

        if referral_response.get("success"):
            rpc.response_len_setter(response_len=1)
            quantity_response = rpc.publish(
                message={
                    "quantity": {
                        "action": "add_to_reserve_dealership",
                        "body": {
                            "referral_number": referral_response.get("message"),
                            "customer_id": str(user.get("user_id")),
                            "customer_type": user.get("customer_type"),
                            "data": data.json(),
                        }
                    }
                },
                headers={'quantity': True}
            ).get("quantity", {})
            print(quantity_response)
            if quantity_response.get("success"):
                return quantity_response
            return quantity_response
        return {"success": False, "message": "Dealership: referral number is not generated."}
        # raise HTTPException(status_code=quantity_response.get("status_code", 500),
        #                     detail={"error": quantity_response.get("error", "Dealership service Internal error")})