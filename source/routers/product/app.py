from fastapi import FastAPI, responses
from starlette.exceptions import HTTPException as starletteHTTPException

from source.config import settings
# from source.routers.product.controllers.custom_category_controller import router as custom_category_controller
# from source.routers.product.controllers.kowsar_controller import router as kowsar_controller
# from source.routers.product.controllers.product_controller import router as product_controller
from source.routers.product.controllers.new_product_controller import router as new_product_controller

TAGS = [
    {
        "name": "Product",
        "description": "Product CRUD"
    }
]
app = FastAPI(
    title="Product API",
    description="This is Product gateway MicroService",
    version="0.1.0",
    openapi_tags=TAGS,
    docs_url="/docs/" if settings.DEBUG_MODE else None,
    redoc_url="/redoc/" if settings.DEBUG_MODE else None,
    debug=settings.DEBUG_MODE
)


# customize exception handler of fast api
@app.exception_handler(starletteHTTPException)
def validation_exception_handler(request, exc):
    return responses.JSONResponse(exc.detail, status_code=exc.status_code)


#
# app.include_router(product_controller)
# app.include_router(kowsar_controller)
# app.include_router(custom_category_controller)
app.include_router(new_product_controller)
