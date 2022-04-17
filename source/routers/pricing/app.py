from typing import Optional

from fastapi import FastAPI, HTTPException, Response, responses, Path
from starlette.exceptions import HTTPException as starletteHTTPException

from source.config import settings
from source.helpers.case_converter import convert_case
from source.message_broker.rabbit_server import RabbitRPC
from source.routers.pricing.validators.pricing_validator import Price

TAGS = [
    {
        "name": "Pricing",
        "description": "Service for setting prices of the products according to customer's types and storages"
    }
]
app = FastAPI(
    title="Pricing API",
    description="This is Pricing gateway MicroService",
    version="0.1.0",
    openapi_tags=TAGS,
    docs_url="/docs/",
    redoc_url="/redoc/",
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


@app.get("/product/price_page/{systemCode}/", tags=["Pricing"])
def get_product_price_page(response: Response,
                           system_code: str = Path(..., alias="systemCode", max_length=12, min_length=12),
                           lang: Optional[str] = "fa_ir"):
    """
    get product price page
    """
    rpc.response_len_setter(response_len=2)
    price_page = rpc.publish(
        message={
            "product": {
                "action": "get_product_child",
                "body": {
                    "system_code": system_code,
                    "lang": lang
                }
            }, "pricing": {
                "action": "get_price_child",
                "body": {
                    "system_code": system_code
                }
            }}
        ,
        headers={"product": True, "pricing": True}
    )
    product_result = price_page.get("product", {})
    pricing_result = price_page.get("pricing", {})
    if product_result.get("success"):
        response.status_code = product_result.get("status_code", 200)
        if product_result.get("message", {}).get("product", {}).get("step") >= 3:
            return convert_case({
                "product": product_result.get("message"),
                "pricing": pricing_result.get("message", {}).get("products", {}).get(system_code, None)
            }, 'camel')
        raise HTTPException(status_code=409, detail={"error": "Product is not in the correct step"})

    raise HTTPException(status_code=product_result.get("status_code", 500),
                        detail={"error": product_result.get("error", "something went wrong")})


@app.post("/product/price/", tags=["Pricing"])
def set_product_price(item: Price, response: Response) -> dict:
    """
    set product(12 digits) price according to customer type and warehouse
    priority of each price is like this:
    1. Special price of warehouse
    2. Price of warehouse
    3. Special price of customer type
    4. Price of customer type
    5. Special price of all
    6. Price of all
    """
    rpc.response_len_setter(response_len=1)
    pricing_result = rpc.publish(
        message={
            "pricing": {
                "action": "set_price",
                "body": item.get()
            }
        },
        headers={'pricing': True}
    )
    pricing_result = pricing_result.get("pricing", {})
    if pricing_result.get("success"):
        if pricing_result.get("message", {}) == "price set successfully":
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
        response.status_code = pricing_result.get("status_code", 200)
        return {"message": pricing_result.get("message")}
    raise HTTPException(status_code=pricing_result.get("status_code", 500),
                        detail={"error": pricing_result.get("error", "Something went wrong")})


@app.get("/product/price/{systemCode}/", tags=["Pricing"])
def get_product_price(response: Response,
                      system_code: str = Path(..., min_length=11, max_length=11, alias='systemCode')) -> dict:
    """
    get product price
    """
    rpc.response_len_setter(response_len=1)
    pricing_result = rpc.publish(
        message={
            "pricing": {
                "action": "get_price",
                "body": {
                    "system_code": system_code
                }
            }
        },
        headers={'pricing': True}
    )
    pricing_result = pricing_result.get("pricing", {})
    if pricing_result.get("success"):
        response.status_code = pricing_result.get("status_code", 200)
        return convert_case(pricing_result.get("message"), 'camel')
    raise HTTPException(status_code=pricing_result.get("status_code", 500),
                        detail={"error": pricing_result.get("error", "Something went wrong")})
