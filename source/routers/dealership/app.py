from fastapi import FastAPI, responses
from source.config import settings
from starlette.exceptions import HTTPException as starletteHTTPException
from source.routers.dealership.controllers.registration_goods_request import router as post_api
from source.routers.dealership.controllers.get_warehouse import router as get_api



TAGS = [
    {
        "name": "Dealership",
        "description": "Dealership application endpoints"
    }
]
app = FastAPI(
    title="Dealership API service",
    description="This is Dealership gateway MicroService",
    version="0.1.0",
    openapi_tags=TAGS,
    docs_url="/docs/",
    redoc_url="/redoc/",
    debug=settings.DEBUG_MODE
)


# @app.exception_handler(starletteHTTPException)
# def validation_exception_handler(request, exc):
#     return responses.JSONResponse(exc.detail, status_code=exc.status_code)


app.include_router(post_api)
app.include_router(get_api)