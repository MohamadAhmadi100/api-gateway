from fastapi import FastAPI, HTTPException, Response, responses
from source.config import settings
from starlette.exceptions import HTTPException as starletteHTTPException
from source.message_broker.rabbit_server import RabbitRPC
from source.routers.shipment.validators.shipment import Shipment



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


@app.post("/get_price", tags=["Calculate shipment price"])
def cities(data: Shipment, response: Response):
    print(data)
    print(type(data))
    rpc.response_len_setter(response_len=1)
    shipment_response = rpc.publish(
        message={
            "shipment": {
                "action": "get_shipment_details",
                "body": {
                    "data": data.json()
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
