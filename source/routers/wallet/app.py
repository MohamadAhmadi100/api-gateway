"""
* this rout is for wallet that have two branch(back office side/ customer side)
* in this rout all of customers data get in token
* all of api objects first validated in "validators" directory then send to services
"""
from fastapi import FastAPI, responses
from starlette.exceptions import HTTPException as starletteHTTPException
from source.config import settings
from source.routers.wallet.controllers.other_controllers import router as other_router
from source.routers.wallet.controllers.charge_wallet_controller import router as charge_router
from starlette_prometheus import metrics, PrometheusMiddleware

TAGS = [
    {
        "name": "Wallet",
        "description": "Wallet application endpoints"
    }
]
app = FastAPI(
    title="Wallet API service",
    description="This is Wallet gateway MicroService",
    version="0.1.0",
    openapi_tags=TAGS,
    docs_url="/docs/" if settings.DEBUG_MODE else None,
    redoc_url="/redoc/" if settings.DEBUG_MODE else None,
    debug=settings.DEBUG_MODE
)


@app.exception_handler(starletteHTTPException)
def validation_exception_handler(request, exc):
    return responses.JSONResponse(exc.detail, status_code=exc.status_code)

app.add_middleware(PrometheusMiddleware)
app.add_route('/metrics', metrics)

app.include_router(charge_router)
app.include_router(other_router)
