from fastapi import FastAPI, responses
from starlette.exceptions import HTTPException as starletteHTTPException
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from source.config import settings
from source.routers.payment.controllers.bank_controller import router as bank_controller
from source.routers.payment.controllers.kowsar_controller import router as kowsar_controller
from starlette_prometheus import metrics, PrometheusMiddleware

TAGS = [
    {
        "name": "Payment",
        "description": "Payment Application Endpoints"
    }
]

app = FastAPI(
    title="Payment API",
    description="This is Payment gateway MicroService",
    version="0.1.0",
    openapi_tags=TAGS,
    docs_url="/docs/" if settings.DEBUG_MODE else None,
    redoc_url="/redoc/" if settings.DEBUG_MODE else None,
    debug=settings.DEBUG_MODE
)

app.add_middleware(
    TrustedHostMiddleware, allowed_hosts=["*"]
)
app.add_middleware(PrometheusMiddleware)
app.add_route('/metrics', metrics)

@app.exception_handler(starletteHTTPException)
def validation_exception_handler(request, exc):
    return responses.JSONResponse(exc.detail, status_code=exc.status_code)


app.include_router(bank_controller)
app.include_router(kowsar_controller)
