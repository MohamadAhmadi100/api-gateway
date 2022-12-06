from fastapi import FastAPI, responses
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette_prometheus import metrics, PrometheusMiddleware
from source.config import settings
from source.routers.gallery.controllers.directories_controller import router as directories_controller
from source.routers.gallery.controllers.file_type_controller import router as file_type_controller
from source.routers.gallery.controllers.files_controller import router as files_controller

TAGS = [
    {
        "name": "File Types",
        "description": "Managing File Types"
    },
    {
        "name": "Directories",
        "description": "Managing Directories"
    },
    {
        "name": "Files",
        "description": "Working With Files"
    }
]

app = FastAPI(
    title="Gallery API",
    description="This is Gallery MicroService for managing uploads",
    version="0.1.0",
    docs_url="/docs/" if settings.DEBUG_MODE else None,
    redoc_url="/redoc/" if settings.DEBUG_MODE else None,
    openapi_tags=TAGS
)


# customize exception handler of fast api
@app.exception_handler(StarletteHTTPException)
def validation_exception_handler(request, exc):
    return responses.JSONResponse(exc.detail, status_code=exc.status_code)


app.include_router(files_controller, tags=['Files'])
app.include_router(file_type_controller, tags=['File Types'])
app.include_router(directories_controller, tags=['Directories'])

app.add_middleware(PrometheusMiddleware)
app.add_route('/metrics', metrics)