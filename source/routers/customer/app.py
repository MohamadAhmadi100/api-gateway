from starlette_prometheus import PrometheusMiddleware, metrics
from fastapi import FastAPI
from fastapi import responses
from starlette.exceptions import HTTPException as starletteHTTPException

from source.config import settings
# from source.routers.customer.controllers.router_backoffice import router_portal
from source.routers.customer.controllers.router_auth import router_auth
from source.routers.customer.controllers.router_dealership import router_dealership
from source.routers.customer.controllers.router_register import router_register
from source.routers.customer.controllers.router_profile import router_profile
from source.routers.customer.controllers.router_rakiano import router_rakiano


app = FastAPI(
    version="0.1.0",
    title="Customer API",
    description="This is Customer gateway MicroService",
    docs_url="/docs/" if settings.DEBUG_MODE else None,
    redoc_url="/redoc/" if settings.DEBUG_MODE else None,
    debug=settings.DEBUG_MODE
)

app.add_middleware(PrometheusMiddleware)
app.add_route("/metrics", metrics)

app.include_router(router_auth)
app.include_router(router_register)
app.include_router(router_profile)
app.include_router(router_dealership)
app.include_router(router_rakiano)


@app.exception_handler(starletteHTTPException)
def validation_exception_handler(request, exc):
    return responses.JSONResponse(exc.detail, status_code=exc.status_code)
