from fastapi import FastAPI
from fastapi import responses
from starlette.exceptions import HTTPException as starletteHTTPException
from source.routers.kosar.controllers import customer_router
from source.config import settings
from starlette_prometheus import metrics, PrometheusMiddleware

app = FastAPI(
    version="0.1.0",
    title="Kosar API",
    description="This is Kosar gateway MicroService",
    docs_url="/docs/" if settings.DEBUG_MODE else None,
    redoc_url="/redoc/" if settings.DEBUG_MODE else None,
    debug=settings.DEBUG_MODE
)

# app.include_router(customer_router)

app.add_middleware(PrometheusMiddleware)
app.add_route('/metrics', metrics)

@app.exception_handler(starletteHTTPException)
def validation_exception_handler(request, exc):
    return responses.JSONResponse(exc.detail, status_code=exc.status_code)
