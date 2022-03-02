from fastapi import FastAPI, HTTPException, Response, responses, Depends
from starlette.exceptions import HTTPException as starletteHTTPException
from source.config import settings
from source.message_broker.rabbit_server import RabbitRPC
from source.routers.wallet.validators.wallet import Wallet
from source.routers.wallet.validators.transaction import Transaction
from source.routers.wallet.validators.update_wallet import UpdateData
from source.routers.customer.module.auth import AuthHandler

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


# --------------------------------- start back-office endpoints -------------------------------------- #
@app.post("/", tags=["back office side"])
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


@app.get("/", tags=["back office side"])
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


auth_handler = AuthHandler()


@app.put("/", tags=["back office side"])
def update_wallet(data: UpdateData, response: Response,
                  auth_header=Depends(auth_handler.check_current_user_tokens)):
    data, token_dict = auth_header
    print(data + "**********")
    print(token_dict + "**********")
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


@app.post("/transactions", tags=["back office side"])
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


# --------------------------------- end back-office endpoints -------------------------------------- #
# ---------------------------------- start customer endpoints -------------------------------------- #

@app.get("/transaction", tags=["customer side"])
def get_transaction(data: Transaction, response: Response):
    rpc.response_len_setter(response_len=1)
    wallet_response = rpc.publish(
        message={
            "wallet": {
                "action": "customer_get_transaction",
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


# ----------------------------------- end customer endpoints --------------------------------------- #
auth = AuthHandler()


@app.get("/get-wallet", tags=["edit_wallet_by_customer_id"])
def get_wallet_by_customer_id(
        response: Response,
        auth_header=Depends(auth.check_current_user_tokens)
):
    customer_id, token_dict = auth_header

    response.headers["accessToken"] = token_dict.get("access_token")
    response.headers["refreshToken"] = token_dict.get("refresh_token")
    rpc.response_len_setter(response_len=1)
    wallet_response = rpc.publish(
        message={
            "wallet": {
                "action": "customer_get_wallet",
                "body": {
                    "customer_id": customer_id.get("customer_id")
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
