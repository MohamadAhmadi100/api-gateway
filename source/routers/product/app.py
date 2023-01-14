from fastapi import FastAPI, responses
from starlette.exceptions import HTTPException as starletteHTTPException

from source.config import settings
from source.routers.product.controllers.product_controller import router as product_controller

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


app.include_router(product_controller)
