from fastapi import FastAPI, HTTPException, Response, responses, Depends
from starlette.exceptions import HTTPException as starletteHTTPException
from source.config import settings
from source.message_broker.rabbit_server import RabbitRPC
from source.routers.wallet.validators.wallet import Wallet
from source.routers.wallet.validators.transaction import Transaction
from source.routers.wallet.validators.update_wallet import UpdateData
from source.routers.customer.module.auth import AuthHandler
from source.routers.wallet.validators.charge_wallet import Charge
from source.routers.payment.modules import payment_modules


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
@app.post("/", tags=["back-office side"])
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


@app.get("/", tags=["back-office side"])
def get_wallet(customerId: int, response: Response):
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


@app.put("/update_wallet", tags=["back-office side"])
def update_wallet(data: UpdateData, response: Response,):
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


@app.get("/transactions", tags=["back-office side"])
def get_transactions(response: Response, data: Transaction = Depends(),
                     auth_header=Depends(auth_handler.check_current_user_tokens)):
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
auth = AuthHandler()


@app.get("/transaction", tags=["customer side"])
def get_transaction(response: Response, data: Transaction = Depends()):
    auth_header = AuthHandler()
    phone_number, token_dict = auth_header
    rpc.response_len_setter(response_len=1)
    wallet_response = rpc.publish(
        message={
            "wallet": {
                "action": "customer_get_transaction",
                "body": {
                    "data": data,
                    "customer":
                        {"customer_id": "customer_id", "phone_number": phone_number}
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


@app.get("/get-wallet", tags=["customer side"])
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

# ----------------------------------- end customer endpoints --------------------------------------- #



@app.put("/charge_wallet", tags=["charge wallet amount"])
def charge_wallet(
        charge_data: Charge,
        response: Response,
):
    # auth_header = Depends(auth.check_current_user_tokens)
    # customer_id, token_dict = auth_header
    #
    # response.headers["accessToken"] = token_dict.get("access_token")
    # response.headers["refreshToken"] = token_dict.get("refresh_token")
    rpc.response_len_setter(response_len=1)
    wallet_response = rpc.publish(
        message={
            "wallet": {
                "action": "create_transaction",
                "body": {
                    "data": {
                        "customer_id": charge_data.customer_id,
                        "action_type": charge_data.action_type,
                        "amount": charge_data.amount,
                        "payment_method": charge_data.payment_method,
                        "balance": charge_data.balance,
                        "wallet_id": charge_data.wallet_id,
                        "process_type": charge_data.process_type,
                        "type": charge_data.type
                    }
                }
            },
        },
        headers={'wallet': True}
    ).get("wallet", {})

    if wallet_response.get("success"):
        transaction = wallet_response.get("message")
        rpc.response_len_setter(response_len=1)
        payment_result = rpc.publish(
            message={
                "payment": {
                    "action": "get_data",
                    "body": {
                        "data": {
                            "amount": charge_data.amount,
                            "bank_name": charge_data.bank_name,
                            "customer_id": charge_data.customer_id,
                            "service": {
                                "service_name": "wallet",
                                "service_function": "charge_wallet"
                            },
                            "order_id": transaction.get("transactionId")
                        }
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