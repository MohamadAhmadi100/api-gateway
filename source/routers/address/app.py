from fastapi import FastAPI, HTTPException, Response, responses
from source.config import settings
from starlette.exceptions import HTTPException as starletteHTTPException
from source.message_broker.rabbit_server import RabbitRPC
from source.routers.address.validators.address import Address
from source.routers.address.validators.update_address import UpdateAddress

TAGS = [
    {
        "name": "Address",
        "description": "Address application endpoints"
    }
]
app = FastAPI(
    title="Address API service",
    description="This is Address gateway MicroService",
    version="0.1.0",
    openapi_tags=TAGS,
    docs_url="/api/v1/docs/",
    redoc_url="/api/v1/redoc/",
    debug=settings.DEBUG_MODE
)


@app.exception_handler(starletteHTTPException)
def validation_exception_handler(request, exc):
    return responses.JSONResponse(exc.detail, status_code=exc.status_code)


rpc = RabbitRPC(exchange_name='headers_exchange', timeout=5)
rpc.connect()
rpc.consume()


@app.get("/states", tags=["City and States"])
def states(response: Response):
    rpc.response_len_setter(response_len=1)
    address_response = rpc.publish(
        message={
            "address": {
                "action": "states",
                "body": {}
            }
        },
        headers={'address': True}
    ).get("address", {})

    if address_response.get("success"):
        response.status_code = address_response.get("status_code", 200)
        return address_response
    raise HTTPException(status_code=address_response.get("status_code", 500),
                        detail={"error": address_response.get("error", "Address service Internal error")})



@app.get("/cities", tags=["City and States"])
def cities(CityId: str, response: Response):
    rpc.response_len_setter(response_len=1)
    address_response = rpc.publish(
        message={
            "address": {
                "action": "cities",
                "body": {
                    "CityId": CityId
                }
            }
        },
        headers={'address': True}
    ).get("address", {})

    if address_response.get("success"):
        response.status_code = address_response.get("status_code", 200)
        return address_response
    raise HTTPException(status_code=address_response.get("status_code", 500),
                        detail={"error": address_response.get("error", "Address service Internal error")})



@app.post("/create", tags=["Address"])
def create_address(data: Address, response: Response):
    rpc.response_len_setter(response_len=1)
    address_response = rpc.publish(
        message={
            "address": {
                "action": "insert_address",
                "body": {
                    "data": dict(data)
                }
            }
        },
        headers={'address': True}
    ).get("address", {})

    if address_response.get("success"):
        response.status_code = address_response.get("status_code", 201)
        return address_response
    raise HTTPException(status_code=address_response.get("status_code", 500),
                        detail={"error": address_response.get("error", "Address service Internal error")})




@app.put("/update_fields", tags=["Address"])
def update_address(data: UpdateAddress, response: Response):
    rpc.response_len_setter(response_len=1)
    address_response = rpc.publish(
        message={
            "address": {
                "action": "update_address",
                "body": {
                    "data": dict(data)
                }
            }
        },
        headers={'address': True}
    ).get("address", {})

    if address_response.get("success"):
        response.status_code = address_response.get("status_code", 200)
        return address_response
    raise HTTPException(status_code=address_response.get("status_code", 500),
                        detail={"error": address_response.get("error", "Address service Internal error")})



@app.get("/customer_addresses", tags=["Address"])
def cities(customerId: str, response: Response):
    rpc.response_len_setter(response_len=1)
    address_response = rpc.publish(
        message={
            "address": {
                "action": "get_customer_addresses",
                "body": {
                    "customerId": customerId
                }
            }
        },
        headers={'address': True}
    ).get("address", {})

    if address_response.get("success"):
        response.status_code = address_response.get("status_code", 200)
        return address_response
    raise HTTPException(status_code=address_response.get("status_code", 500),
                        detail={"error": address_response.get("error", "Address service Internal error")})



