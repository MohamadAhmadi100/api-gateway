from fastapi import FastAPI, HTTPException, Response, responses, Depends
from starlette.exceptions import HTTPException as starletteHTTPException
from source.config import settings
from source.message_broker.rabbit_server import RabbitRPC
from source.routers.wallet.validators.wallet import Wallet
from source.routers.wallet.validators.transaction import Transaction
from source.routers.wallet.validators.update_wallet import UpdateData

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
    docs_url="/api/v1/docs/",
    redoc_url="/api/v1/redoc/",
    debug=settings.DEBUG_MODE
)


@app.exception_handler(starletteHTTPException)
def validation_exception_handler(request, exc):
    return responses.JSONResponse(exc.detail, status_code=exc.status_code)


rpc = RabbitRPC(exchange_name='headers_exchange', timeout=5)
rpc.connect()
rpc.consume()


@app.post("/create", tags=["wallet_create"])
def create_wallet(data: Wallet, response: Response) -> None:
    rpc.response_len_setter(response_len=1)
    wallet_response = rpc.publish(
        message={
            "wallet": {
                "action": "create_wallet",
                "body": {
                    "data": dict(data)
                }
            }
        },
        headers={'wallet': True}
    ).get("wallet", {})
    if wallet_response.get("success"):
        response.status_code = wallet_response.get("status_code", 200)
        return wallet_response
    raise HTTPException(status_code=wallet_response.get("status_code", 500),
                        detail={"error": wallet_response.get("error", "Wallet service Internal error")})


@app.get("/wallet_details", tags=["get_wallet"])
def get_wallet(customerId: int, response: Response):
    print(customerId)
    rpc.response_len_setter(response_len=1)
    wallet_response = rpc.publish(
        message={
            "wallet": {
                "action": "get_wallet",
                "body": {
                    "data": int(customerId)
                }
            }
        },
        headers={'wallet': True}
    ).get("wallet", {})

    if wallet_response.get("success"):
        response.status_code = wallet_response.get("status_code", 200)
        return wallet_response
    raise HTTPException(status_code=wallet_response.get("status_code", 500),
                        detail={"error": wallet_response.get("error", "Wallet service Internal error")})


@app.put("/update", tags=["edit_wallet_data"])
def update_wallet(data: UpdateData, response: Response):
    print(data)
    rpc.response_len_setter(response_len=1)
    wallet_response = rpc.publish(
        message={
            "wallet": {
                "action": "update_wallet",
                "body": {
                    "data": dict(data)
                }
            }
        },
        headers={'wallet': True}
    ).get("wallet", {})

    if wallet_response.get("success"):
        response.status_code = wallet_response.get("status_code", 200)
        return wallet_response
    raise HTTPException(status_code=wallet_response.get("status_code", 500),
                        detail={"error": wallet_response.get("error", "Wallet service Internal error")})


@app.post("/transactions_details", tags=["transactions"])
def gte_transactions(data: Transaction, response: Response):
    rpc.response_len_setter(response_len=1)
    wallet_response = rpc.publish(
        message={
            "wallet": {
                "action": "get_transaction",
                "body": {
                    "data": dict(data)
                }
            }
        },
        headers={'wallet': True}
    ).get("wallet", {})
    if wallet_response.get("success"):
        response.status_code = wallet_response.get("status_code", 200)
        return wallet_response
    raise HTTPException(status_code=wallet_response.get("status_code", 500),
                        detail={"error": wallet_response.get("error", "Wallet service Internal error")})
