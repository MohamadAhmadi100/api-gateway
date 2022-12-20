from fastapi import FastAPI
from fastapi import responses
from starlette.exceptions import HTTPException as starletteHTTPException
from starlette_prometheus import PrometheusMiddleware, metrics

from source.config import settings
from source.routers.coupon.controllers.router_coupon import router_coupon

app = FastAPI(
    version="0.1.0",
    title="Coupon API",
    description="This is Coupon gateway MicroService",
    docs_url="/docs/" if settings.DEBUG_MODE else None,
    redoc_url="/redoc/" if settings.DEBUG_MODE else None,
    debug=settings.DEBUG_MODE
)
app.add_middleware(PrometheusMiddleware)
app.add_route("/metrics", metrics)

app.include_router(router_coupon)


@app.exception_handler(starletteHTTPException)
def validation_exception_handler(request, exc):
    return responses.JSONResponse(exc.detail, status_code=exc.status_code)
