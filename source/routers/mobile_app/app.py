from fastapi import FastAPI, responses
from starlette.exceptions import HTTPException as starletteHTTPException
from source.routers.mobile_app.controllers.app_controller import router as app_router
from source.routers.mobile_app.controllers.football_controller import router as football_router

from source.config import settings

TAGS = [
    {
        "name": "ForceUpdate",
        "description": "ForceUpdate CRUD"
    }
]

app = FastAPI(
    title="Mobile App API",
    description="This is ForceUpdate gateway MicroService",
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


app.include_router(app_router)
app.include_router(football_router)
