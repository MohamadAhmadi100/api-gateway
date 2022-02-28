from fastapi import FastAPI, HTTPException, Response, responses, Path
from starlette.exceptions import HTTPException as starletteHTTPException

from source.config import settings
from source.helpers.case_converter import convert_case
from source.message_broker.rabbit_server import RabbitRPC
from source.routers.quantity.validators.quantity import Quantity

TAGS = [
    {
        "name": "Quantity",
        "description": "Quantity CRUD"
    }
]
app = FastAPI(
    title="Quantity API",
    description="This is Quantity gateway MicroService",
    version="0.1.0",
    openapi_tags=TAGS,
    docs_url="/api/v1/docs/",
    redoc_url="/api/v1/redoc/",
    debug=settings.DEBUG_MODE
)


# customize exception handler of fast api
@app.exception_handler(starletteHTTPException)
def validation_exception_handler(request, exc):
    return responses.JSONResponse(exc.detail, status_code=exc.status_code)


# initialize rabbit mq
rpc = RabbitRPC(exchange_name='headers_exchange', timeout=5)
rpc.connect()
rpc.consume()


@app.post("/api/v1/product/quantity/", tags=["Quantity"])
def set_product_quantity(item: Quantity, response: Response) -> dict:
    """
    set product(12 digits) quantity according to customer type and warehouse
    priority of each quantity is like this:
    1. Stock for sale of warehouse
    2. Stock for sale of customer type
    3. Stock for sale of all
    """
    rpc.response_len_setter(response_len=1)
    b = item.get()
    a = convert_case(item.get(), action='snake')
    quantity_result = rpc.publish(
        message={
            "quantity": {
                "action": "set_quantity",
                "body": item.get()
            }
        },
        headers={'quantity': True}
    )
    quantity_result = quantity_result.get("quantity", {})
    if quantity_result.get("success"):
        rpc.publish(
            message={
                "product": {
                    "action": "step_up_product",
                    "body": {
                        "system_code": item.system_code
                    }
                }
            },
            headers={"product": True}
        )
        response.status_code = quantity_result.get("status_code", 200)
        return {"message": quantity_result.get("message")}
    raise HTTPException(status_code=quantity_result.get("status_code", 500),
                        detail={"error": quantity_result.get("error", "Something went wrong")})


@app.get("/api/v1/product/quantity/{systemCode}/", tags=["Quantity"])
def get_product_quantity(response: Response,
                         system_code: str = Path(..., min_length=11, max_length=11, alias="systemCode")) -> dict:
    """
    get product quantity
    """
    rpc.response_len_setter(response_len=1)
    quantity_result = rpc.publish(
        message={
            "quantity": {
                "action": "get_quantity",
                "body": {
                    "system_code": system_code
                }
            }
        },
        headers={'quantity': True}
    )
    quantity_result = quantity_result.get("quantity", {})
    if quantity_result.get("success"):
        response.status_code = quantity_result.get("status_code", 200)
        return convert_case(quantity_result.get("message"), action='camel')
    raise HTTPException(status_code=quantity_result.get("status_code", 500),
                        detail={"error": quantity_result.get("error", "Something went wrong")})


@app.get("/api/v1/product/{systemCode}/stock/", tags=["Quantity"])
def get_product_stock(response: Response,
                      system_code: str = Path(..., min_length=12, max_length=12, alias="systemCode")) -> dict:
    """
    get product stock
    """
    rpc.response_len_setter(response_len=1)
    quantity_result = rpc.publish(
        message={
            "quantity": {
                "action": "get_stock",
                "body": {
                    "system_code": system_code
                }
            }
        },
        headers={'quantity': True}
    )
    quantity_result = quantity_result.get("quantity", {})
    if quantity_result.get("success"):
        response.status_code = quantity_result.get("status_code", 200)
        return convert_case(quantity_result.get("message"), action='camel')
    raise HTTPException(status_code=quantity_result.get("status_code", 500),
                        detail={"error": quantity_result.get("error", "Something went wrong")})
