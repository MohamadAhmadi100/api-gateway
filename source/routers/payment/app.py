from fastapi import FastAPI, HTTPException, Response, responses, Request
from starlette.exceptions import HTTPException as starletteHTTPException
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from source.config import settings
from source.message_broker.rabbit_server import RabbitRPC
from source.routers.payment.validators import payment
from source.routers.payment.modules import payment_modules

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
    docs_url="/docs/",
    redoc_url="/redoc/",
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


@app.post("/send_data")
def get_url(data: payment.SendData, response: Response):
    rpc.response_len_setter(response_len=1)
    payment_result = rpc.publish(
        message={
            "payment": {
                "action": "get_data",
                "body": {
                    "data": dict(data)
                }
            }
        },
        headers={'payment': True}
    )
    payment_result = payment_result.get("payment", {})
    if not payment_result.get("success"):
        raise HTTPException(status_code=payment_result.get("status_code", 500),
                            detail={"error": payment_result.get("error", "Something went wrong")})

    response.status_code = payment_result.get("status_code", 200)
    token_result = payment_modules.request_bank(
        payment_result.get("message", {}).get("url"),
        payment_result.get("message", {}).get("bank_data")
    )
    if not token_result.get("success"):
        raise HTTPException(status_code=token_result.get("status_code", 500),
                            detail={"error": token_result.get("error", "Something went wrong")})
    rpc.response_len_setter(response_len=1)
    check_token_result = rpc.publish(
        message={
            "payment": {
                "action": "check_token",
                "body": {
                    "response": token_result.get("message"),
                    "bank_name": payment_result.get("bank_name")
                }
            }
        },
        headers={'payment': True}
    )
    check_token_result = check_token_result.get("payment", {})
    if not check_token_result.get("success"):
        raise HTTPException(status_code=check_token_result.get("status_code", 500),
                            detail={"error": check_token_result.get("error", "Something went wrong")})
    response.status_code = check_token_result.get("status_code", 200)
    rpc.response_len_setter(response_len=1)
    url_result = rpc.publish(
        message={
            "payment": {
                "action": "redirect_url",
                "body": {
                    "token": token_result,
                    "payment_id": payment_result.get("payment_id"),
                    "bank_name": payment_result.get("bank_name")
                }
            }
        },
        headers={'payment': True}
    )
    url_result = url_result.get("payment", {})
    if not url_result.get("success"):
        raise HTTPException(status_code=url_result.get("status_code", 500),
                            detail={"error": url_result.get("error", "Something went wrong")})
    response.status_code = url_result.get("status_code", 200)
    return url_result.get("message")


@app.post("/callback")
async def set_callback(request: Request, response: Response):
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
    if not payment_result.get("success"):
        raise HTTPException(status_code=payment_result.get("status_code", 500),
                            detail={"error": payment_result.get("error", "Something went wrong")})
    response.status_code = payment_result.get("status_code", 200)
    response.status_code = payment_result.get("status_code", 200)
    verify_result = payment_modules.request_bank(
        payment_result.get("message", {}).get("url"),
        payment_result.get("message", {}).get("bank_data")
    )
    if not verify_result:
        raise HTTPException(status_code=verify_result.get("status_code", 500),
                            detail={"error": verify_result.get("error", "Something went wrong")})
    response.status_code = verify_result.get("status_code", 200)
    rpc.response_len_setter(response_len=1)
    check_verify = rpc.publish(
        message={
            "payment": {
                "action": "check_verify",
                "body": {
                    "data": verify_result.get("message"),
                    "token": payment_result.get("token"),
                    "bank_name": payment_result.get("message", {}).get("bank_name")
                }
            }
        },
        headers={'payment': True}
    )
    check_verify = check_verify.get("payment", {})
    if not check_verify.get("success"):
        raise HTTPException(status_code=check_verify.get("status_code", 500),
                            detail={"error": check_verify.get("error", "Something went wrong")})
    response.status_code = check_verify.get("status_code", 200)
    rpc.response_len_setter(response_len=1)
    service_data = rpc.publish(
        message={
            check_verify.get("message", {}).get("service", {}).get("service_name"):
                {
                    "action": check_verify.get("message", {}).get("service", {}).get("service_function"),
                    "body": {
                        "data": check_verify.get("message")
                    }
                }
        },
        headers={check_verify.get("message", {}).get("service", {}).get("service_name"): True}
    )
    if not service_data.get("success"):
        raise HTTPException(status_code=service_data.get("status_code", 500),
                            detail={"error": service_data.get("error", "Something went wrong")})
    response.status_code = service_data.get("status_code", 200)
