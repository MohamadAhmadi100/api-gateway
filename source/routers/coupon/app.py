from fastapi import FastAPI, HTTPException, Response, responses, Path, Body, Query
from starlette.exceptions import HTTPException as starletteHTTPException

from source.config import settings
from source.helpers.case_converter import convert_case
from source.message_broker.rabbit_server import RabbitRPC
from source.routers.coupon.controller.router_coupon import router as router_coupon

TAGS = [
    {
        "name": "Coupon",
        "description": "Create, get, update and delete coupons in main collection."
    }
]
app = FastAPI(
    title="Coupon API",
    description="This is Coupon Gateway MicroService",
    version="0.1.0",
    openapi_tags=TAGS,
    docs_url="/api/v1/docs/",
    redoc_url="/api/v1/redoc/",
    debug=settings.DEBUG_MODE
)

app.include_router(router_coupon)


# customize exception handler of fast api
@app.exception_handler(starletteHTTPException)
def validation_exception_handler(request, exc):
    return responses.JSONResponse(exc.detail, status_code=exc.status_code)
