from fastapi import FastAPI, responses
from starlette.exceptions import HTTPException as starletteHTTPException

from source.config import settings
from source.routers.attribute.controllers.assignee_controller import router as assignee_router
from source.routers.attribute.controllers.attribute_controller import router as attribute_router

TAGS_META = [
    {
        "name": "attribute",
        "description": "Create, Read, Update and Delete attributes in main collection.",
    },
    {
        "name": "assignee",
        "description": "Add or remove attribute to a certain collection called assignee."
    }
]

app = FastAPI(title="Custom Attribute",
              description="A microservice to create custom attribute for other microservices!",
              version="0.1.0",
              openapi_tags=TAGS_META,
              docs_url="/docs/" if settings.DEBUG_MODE else None,
              redoc_url="/redoc/" if settings.DEBUG_MODE else None)

app.include_router(assignee_router)
app.include_router(attribute_router)


# customize exception handler of fast api
@app.exception_handler(starletteHTTPException)
def validation_exception_handler(request, exc):
    return responses.JSONResponse(exc.detail, status_code=exc.status_code)
