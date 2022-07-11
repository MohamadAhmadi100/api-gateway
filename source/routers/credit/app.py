from fastapi import FastAPI, responses
from starlette.exceptions import HTTPException as starletteHTTPException

from source.config import settings
from source.routers.credit.controller.credit_router import credit
from source.routers.customer.module.auth import AuthHandler
from source.routers.order.controllers.checkout_step import first_step_order
from source.routers.order.controllers.edit_order import edit_order
from source.routers.order.controllers.final_step import final_step_order
from source.routers.order.controllers.get_orders import get_order
from source.routers.order.controllers.payment_step import payment_step_order
from source.routers.order.controllers.shipment_steps import shipment_step

TAGS = [
    {
        "name": "Order",
        "description": "ORDER CRUD"
    }
]

app = FastAPI(
    title="Order API",
    description="This is order gateway MicroService",
    version="0.1.0",
    openapi_tags=TAGS,
    docs_url="/docs/",
    redoc_url="/redoc/",
    debug=settings.DEBUG_MODE
)

auth_handler = AuthHandler()

app.include_router(credit)



# customize exception handler of fast api
@app.exception_handler(starletteHTTPException)
def validation_exception_handler(request, exc):
    return responses.JSONResponse(exc.detail, status_code=exc.status_code)
