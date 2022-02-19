from fastapi import FastAPI, HTTPException, Response, responses, Request
from starlette.exceptions import HTTPException as starletteHTTPException
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from source.config import settings
from source.message_broker.rabbit_server import RabbitRPC
from source.routers.payment.validators.payment import GetUrl

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
    docs_url="/api/v1/docs/",
    redoc_url="/api/v1/redoc/",
    debug=settings.DEBUG_MODE
)

app.add_middleware(
    TrustedHostMiddleware, allowed_hosts=["*"]
)


@app.exception_handler(starletteHTTPException)
def validation_exception_handler(request, exc):
    return responses.JSONResponse(exc.detail, status_code=exc.status_code)


rpc = RabbitRPC(exchange_name='headers_exchange', timeout=5)
rpc.connect()
rpc.consume()


@app.post("payment/redirect_url")
def get_url(data: GetUrl, response: Response):
    rpc.response_len_setter(response_len=1)
    payment_result = rpc.publish(
        message={
            "payment": {
                "action": "get_url",
                "body": {
                    "data": dict(data)
                }
            }
        },
        headers={'payment': True}
    )
    payment_result = payment_result.get("payment", {})
    if payment_result.get("success"):
        response.status_code = payment_result.get("status_code", 200)
        return payment_result.get("message")
    raise HTTPException(status_code=payment_result.get("status_code", 500),
                        detail={"error": payment_result.get("error", "Something went wrong")})


@app.post("payment/callback")
async def set_callback(request: Request, response=Response):
    rpc.response_len_setter(response_len=1)
    response_string: bytes = await request.body()
    payment_result = rpc.publish(
        message={
            "payment": {
                "action": "callback",
                "body": {
                    "request": response_string
                }
            }
        },
        headers={'payment': True}
    )
    payment_result = payment_result.get("payment", {})
    if payment_result.get("success"):
        response.status_code = payment_result.get("status_code", 200)
        return payment_result.get("message")
    raise HTTPException(status_code=payment_result.get("status_code", 500),
                        detail={"error": payment_result.get("error", "Something went wrong")})
