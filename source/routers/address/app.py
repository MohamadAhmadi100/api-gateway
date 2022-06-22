from fastapi import FastAPI, HTTPException, Response, responses, Depends
from source.config import settings
from starlette.exceptions import HTTPException as starletteHTTPException
from source.message_broker.rabbit_server import RabbitRPC
from source.routers.address.validators.address import Address, AddressId
from source.routers.address.validators.update_address import UpdateAddress
from source.routers.customer.module.auth import AuthHandler

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
    docs_url="/docs/",
    redoc_url="/redoc/",
    debug=settings.DEBUG_MODE
)

auth_handler = AuthHandler()


@app.exception_handler(starletteHTTPException)
def validation_exception_handler(request, exc):
    return responses.JSONResponse(exc.detail, status_code=exc.status_code)


@app.get("/states", tags=["City and States"])
def states(response: Response):
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
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
def cities(cityId: str, response: Response):
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        address_response = rpc.publish(
            message={
                "address": {
                    "action": "cities",
                    "body": {
                        "CityId": cityId
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
def create_address(data: Address,
                   response: Response,
                   auth_header=Depends(auth_handler.check_current_user_tokens)):
    user, token_dict = auth_header
    print(user, token_dict)
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        address_response = rpc.publish(
            message={
                "address": {
                    "action": "insert_address",
                    "body": {
                        "data": dict(data),
                        "customerId": str(user.get("user_id"))
                    }
                }
            },
            headers={'address': True}
        ).get("address", {})

        if address_response.get("success"):
            response.status_code = address_response.get("status_code", 201)
            sub_dict = {
                "user_id": user.get('user_id'),
                "customer_type": user.get('customer_type'),
                "phone_number": user.get('phone_number'),
            }
            response.headers["refreshToken"] = auth_handler.encode_refresh_token(sub_dict)
            response.headers["accessToken"] = auth_handler.encode_access_token(sub_dict)
            return address_response
        raise HTTPException(status_code=address_response.get("status_code", 500),
                            detail={"error": address_response.get("error", "Address service Internal error")})


@app.put("/update_fields", tags=["Address"])
def update_address(data: UpdateAddress,
                   response: Response,
                   auth_header=Depends(auth_handler.check_current_user_tokens)):
    user, token_dict = auth_header
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        address_response = rpc.publish(
            message={
                "address": {
                    "action": "update_address",
                    "body": {
                        "data": dict(data),
                        "customerId": str(user.get("user_id"))
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
def customer_addresses(response: Response,
                       auth_header=Depends(auth_handler.check_current_user_tokens)):
    user, token_dict = auth_header
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        address_response = rpc.publish(
            message={
                "address": {
                    "action": "get_customer_addresses",
                    "body": {
                        "customerId": str(user.get("user_id"))
                    }
                }
            },
            headers={'address': True}
        ).get("address", {})

        if address_response.get("success"):
            response.status_code = address_response.get("status_code", 200)
            return address_response
        return address_response
        # raise HTTPException(status_code=address_response.get("status_code", 500),
        #                     detail={"error": address_response.get("error", "Address service Internal error")})


@app.delete("/delete_address", tags=["Address"])
def delete_address(addressId: AddressId, response: Response, auth_header=Depends(auth_handler.check_current_user_tokens)):
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        user, token_dict = auth_header
        rpc.response_len_setter(response_len=1)
        address_response = rpc.publish(
            message={
                "address": {
                    "action": "delete_customer_address",
                    "body": {
                        "customerId": user.get("user_id"),
                        "addressId": int(addressId.address_id)
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



@app.get("/default_address", tags=["Address"])
def customer_addresses(response: Response, auth_header=Depends(auth_handler.check_current_user_tokens)):
    user, token_dict = auth_header
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        address_response = rpc.publish(
            message={
                "address": {
                    "action": "get_default_address",
                    "body": {
                        "customerId": user.get("user_id")
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




@app.get("/warehouses", tags=["get customer warehouses"])
def states(cityId: str, response: Response):
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        address_response = rpc.publish(
            message={
                "address": {
                    "action": "get_stock_by_city_id",
                    "body": {
                        "cityId": cityId
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