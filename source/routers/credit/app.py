from fastapi import FastAPI, responses
from starlette.exceptions import HTTPException as starletteHTTPException

from source.config import settings
from source.routers.credit.dealership.dealership_router import credit
from source.routers.customer.module.auth import AuthHandler

TAGS = [
    {
        "name": "Credit",
        "description": "Credit CRUD"
    }
]

app = FastAPI(
    title="Credit API",
    description="This is credit gateway MicroService",
    version="0.1.0",
    openapi_tags=TAGS,
    docs_url="/docs/" if settings.DEBUG_MODE else None,
    redoc_url="/redoc/" if settings.DEBUG_MODE else None,
    debug=settings.DEBUG_MODE
)

auth_handler = AuthHandler()

app.include_router(credit)



# customize exception handler of fast api
@app.exception_handler(starletteHTTPException)
def validation_exception_handler(request, exc):
    return responses.JSONResponse(exc.detail, status_code=exc.status_code)
