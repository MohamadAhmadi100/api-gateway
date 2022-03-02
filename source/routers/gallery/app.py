import sys

from fastapi import FastAPI, responses
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from source.config import settings
from source.routers.gallery.controllers.directories_controller import router as directories_controller

from source.routers.gallery.controllers.file_type_controller import router as file_type_controller
from source.routers.gallery.controllers.files_controller import router as files_controller

sys.path.append("/home/erfun/pro/gallery_files/")

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
    docs_url="/api/v1/docs/",
    redoc_url="/api/v1/redoc/",
    openapi_tags=TAGS
)


# customize exception handler of fast api
@app.exception_handler(StarletteHTTPException)
def validation_exception_handler(request, exc):
    return responses.JSONResponse(exc.detail, status_code=exc.status_code)


app.mount("/gallery_files/", StaticFiles(directory=settings.GALLERY_DIR), name="gallery_files")

app.include_router(files_controller, tags=['Files'])
app.include_router(file_type_controller, tags=['File Types'])
app.include_router(directories_controller, tags=['Directories'])
