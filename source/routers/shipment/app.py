import json
from starlette_prometheus import metrics, PrometheusMiddleware
from fastapi import FastAPI, HTTPException, Response, responses, Depends, Query
from source.config import settings
from starlette.exceptions import HTTPException as starletteHTTPException
from source.message_broker.rabbit_server import RabbitRPC
from source.routers.shipment.validators.shipment_validator import Shipment
from source.routers.shipment.validators.shipment_per_stock_validator import PerStock
from source.routers.customer.module.auth import AuthHandler
from source.routers.shipment.validators.mahex_validator import WeekDays, MahexShipment

TAGS = [
    {
        "name": "shipment",
        "description": "Shipment application endpoints"
    }
]
app = FastAPI(
    title="Shipment API service",
    description="This is Shipment gateway MicroService",
    version="0.1.0",
    openapi_tags=TAGS,
    docs_url="/docs/" if settings.DEBUG_MODE else None,
    redoc_url="/redoc/" if settings.DEBUG_MODE else None,
    debug=settings.DEBUG_MODE
)

auth_handler = AuthHandler()

app.add_middleware(PrometheusMiddleware)
app.add_route('/metrics', metrics)


@app.exception_handler(starletteHTTPException)
def validation_exception_handler(request, exc):
    return responses.JSONResponse(exc.detail, status_code=exc.status_code)


rpc = RabbitRPC(exchange_name='headers_exchange', timeout=5)
rpc.connect()
rpc.consume()


@app.post("/get_price", tags=["Calculate shipment price"])
def initial_shipment(data: Shipment, response: Response):
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        shipment_response = rpc.publish(
            message={
                "shipment": {
                    "action": "get_shipment_details",
                    "body": {
                        "data": data.dict()
                    }
                }
            },
            headers={'shipment': True}
        ).get("shipment", {})

        if shipment_response.get("success"):
            response.status_code = shipment_response.get("status_code", 200)
            return shipment_response
        raise HTTPException(status_code=shipment_response.get("status_code", 500),
                            detail={"error": shipment_response.get("error", "Shipment service Internal error")})


@app.put("/get_shipment_per_stock", tags=["Get shipment details and insurance per stock"])
def shipment_per_stock(
        response: Response,
        data: PerStock,
        auth_header=Depends(auth_handler.check_current_user_tokens)
):
    user, token_dict = auth_header
    delivery = {
        "deliveryFirstName": data.receiverFirstName,
        "deliveryLastName": data.receiverLastName,
        "deliveryMobileNumber": data.receiverPhoneNumber,
        "deliveryNationalId": data.receiverNationalId,
    }
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        if data.shippingMethod == "aasood":
            rpc.response_len_setter(response_len=1)
            customer_response = rpc.publish(
                message={
                    "customer": {
                        "action": "add_delivery_person",
                        "body": {
                            "data": {
                                "customer_phone_number": user.get("phone_number"),
                                "delivery": json.dumps(delivery),
                            }
                        }
                    }
                },
                headers={'customer': True}
            ).get("customer", {})
        rpc.response_len_setter(response_len=1)
        shipment_response = rpc.publish(
            message={
                "shipment": {
                    "action": "get_selected_method",
                    "body": {
                        "data": data.dict()
                    }
                }
            },
            headers={'shipment': True}
        ).get("shipment", {})
        if shipment_response.get("success"):
            rpc.response_len_setter(response_len=1)
            cart_response = rpc.publish(
                message={
                    "cart": {
                        "action": "add_shipment_to_cart",
                        "body": {
                            "shipment": {
                                "shipment_details": shipment_response.get("message"),
                                "user_id": user.get("user_id")
                            }
                        }
                    }
                },
                headers={'cart': True}
            ).get("cart", {})

            if cart_response.get("success"):
                response.status_code = cart_response.get("status_code", 200)
                return cart_response
            raise HTTPException(status_code=cart_response.get("status_code", 500),
                                detail={"error": cart_response.get("error", "Shipment service Internal error")})


@app.put("/mahex_weekly_limit", tags=["Mahex"])
def change_limit(data: WeekDays, response: Response):
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        shipment_response = rpc.publish(
            message={
                "shipment": {
                    "action": "change_mahex_limit",
                    "body": {
                        "week_data": data.json()
                    }
                }
            },
            headers={'shipment': True}
        ).get("shipment", {})

        if shipment_response.get("success"):
            response.status_code = shipment_response.get("status_code", 200)
            return shipment_response
        raise HTTPException(status_code=shipment_response.get("status_code", 500),
                            detail={"error": shipment_response.get("error", "Shipment service Internal error")})



@app.post("/create_mahex_shipment", tags=["Mahex"])
def create_mahex_shipment(shipment_data: MahexShipment, response: Response):
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        shipment_data = shipment_data.dict()
        rpc.response_len_setter(response_len=1)
        shipment_response = rpc.publish(
            message={
                "shipment": {
                    "action": "create_mahex_shipment",
                    "body": {
                        "shipment_data": shipment_data
                    }
                }
            },
            headers={'shipment': True}
        ).get("shipment", {})
        if shipment_response.get("success"):
            response.status_code = shipment_response.get("status_code", 201)
            return shipment_response
        raise HTTPException(status_code=shipment_response.get("status_code", 500),
                            detail={"success": False, "message": shipment_response.get("message", "Shipment service Internal error")})




@app.get("/get_waybill_number", tags=["Mahex"])
def change_limit(order_number: str, response: Response):
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        shipment_response = rpc.publish(
            message={
                "shipment": {
                    "action": "get_waybill_number",
                    "body": {
                        "order_number": order_number
                    }
                }
            },
            headers={'shipment': True}
        ).get("shipment", {})

        if shipment_response.get("success"):
            response.status_code = shipment_response.get("status_code", 200)
            return shipment_response
        raise HTTPException(status_code=shipment_response.get("status_code", 500),
                            detail={"success": False, "message": shipment_response.get("message", "Shipment service Internal error")})


