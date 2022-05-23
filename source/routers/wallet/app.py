from fastapi import FastAPI, HTTPException, Response, responses, Depends
from starlette.exceptions import HTTPException as starletteHTTPException
from source.config import settings
from source.message_broker.rabbit_server import RabbitRPC
from source.routers.wallet.validators.transaction import Transaction
from source.routers.wallet.validators.wallets import Wallet
from source.routers.wallet.validators.update_wallet import UpdateData
from source.routers.customer.module.auth import AuthHandler
from source.routers.payment.modules import payment_modules
from source.routers.wallet.validators.checkout_wallet import Reserve, ResultOrder, CompleteOrderWallet, ChargeWallet

"""
* this rout is for wallet that have two branch(back office side/ customer side)
* in this rout all of customers data get in token
* all of api objects first validated in "validators" directory then send to services
"""

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
    docs_url="/docs/",
    redoc_url="/redoc/",
    debug=settings.DEBUG_MODE
)
auth = AuthHandler()


@app.exception_handler(starletteHTTPException)
def validation_exception_handler(request, exc):
    return responses.JSONResponse(exc.detail, status_code=exc.status_code)


@app.put("/update-wallet", tags=["back-office side"])
def update_wallet(data: UpdateData, response: Response,
                  auth_header=Depends(auth.check_current_user_tokens)
                  ):
    """
    in this api just staffs could update(consume/charge) customers wallet(without transaction)
    """
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:

        sub_data, token_data = auth_header
        response.headers["accessToken"] = token_data.get("access_token")
        response.headers["refreshToken"] = token_data.get("refresh_token")
        rpc.response_len_setter(response_len=1)

        last_data = dict(data)
        # get customer id and add that to update object
        last_data["customer_id"] = sub_data.get("user_id")
        wallet_response = rpc.publish(
            message={
                "wallet": {
                    "action": "update_wallet",
                    "body": {
                        "data": last_data
                    }
                }
            },
            headers={'wallet': True}
        ).get("wallet", {})

        if wallet_response.get("success"):
            response.status_code = wallet_response.get("status_code", 200)
            return wallet_response
        elif not wallet_response.get("success"):
            response.status_code = wallet_response.get("status_code", 417)
            return wallet_response
        raise HTTPException(status_code=wallet_response.get("status_code", 500),
                            detail={"error": wallet_response.get("error", "Wallet service Internal error")})



@app.post("/transactions-customer", tags=["customer side"])
def get_transactions(response: Response, data: Transaction,
                      auth_header=Depends(auth.check_current_user_tokens)
                      ):
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:

        sub_data, token_data = auth_header
        response.headers["accessToken"] = token_data.get("access_token")
        response.headers["refreshToken"] = token_data.get("refresh_token")
        # by default,the customer id is sent so that customer only has access to own information

        default_filter = [{
            "name": "customerId",
            "value": str(sub_data.get("user_id"))
        }]

        last_data = dict(data)
        if last_data["filters"]:
            last_data["filters"].append(default_filter[0])
        else:
            last_data["filters"] = default_filter

        rpc.response_len_setter(response_len=1)
        wallet_response = rpc.publish(
            message={
                "wallet": {
                    "action": "get_transactions",
                    "body": {
                        "data": last_data,
                    }
                }
            },
            headers={'wallet': True}
        ).get("wallet", {})

        if wallet_response.get("success"):
            response.status_code = wallet_response.get("status_code", 200)
            return wallet_response
        elif not wallet_response.get("success"):
            response.status_code = wallet_response.get("status_code", 417)
            return wallet_response
        raise HTTPException(status_code=wallet_response.get("status_code", 500),
                            detail={"error": wallet_response.get("error", "Wallet service Internal error")})


@app.get("/customer-wallet", tags=["customer side"])
def get_wallet_by_customer_id_(
        response: Response,
        auth_header=Depends(auth.check_current_user_tokens)
):
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        sub_data, token_data = auth_header
        response.headers["accessToken"] = token_data.get("access_token")
        response.headers["refreshToken"] = token_data.get("refresh_token")
        rpc.response_len_setter(response_len=1)

        wallet_response = rpc.publish(
            message={
                "wallet": {
                    "action": "get_wallet_by_customer_id",
                    "body": {
                        "data": sub_data.get("user_id")
                    }
                }
            },
            headers={'wallet': True}
        ).get("wallet", {})

        if wallet_response.get("success"):
            response.status_code = wallet_response.get("status_code", 200)
            return wallet_response
        elif not wallet_response.get("success"):
            response.status_code = wallet_response.get("status_code", 417)
            return wallet_response
        raise HTTPException(status_code=wallet_response.get("status_code", 500),
                            detail={"error": wallet_response.get("error", "Wallet service Internal error")})


@app.put("/charge_wallet", tags=["customer side"])
def charge_wallet(
        charge_data: ChargeWallet,
        response: Response,
):
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:

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
            token_result = payment_modules.request_bank_handler(
                payment_result.get("message", {}).get("url"),
                payment_result.get("message", {}).get("bank_data"),
                payment_result.get("message", {}).get("bank_name")
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
                            "bank_name": payment_result.get("message", {}).get("bank_name")
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
                            "data": check_token_result.get("message", {}),
                            "payment_id": payment_result.get("message", {}).get("payment_id"),
                            "bank_name": payment_result.get("message", {}).get("bank_name")
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


@app.post("/reserve-wallet", tags=["customer side"])
def reserve_wallet(data: Reserve, response: Response,
                   auth_header=Depends(auth.check_current_user_tokens)
                   ):
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:

        sub_data, token_data = auth_header
        response.headers["accessToken"] = token_data.get("access_token")
        response.headers["refreshToken"] = token_data.get("refresh_token")
        rpc.response_len_setter(response_len=1)

        # get customer data from token and send that for create wallet
        last_data = dict(data)
        # get customer id and add that to update object
        last_data["customer_id"] = sub_data.get("user_id")

        wallet_response = rpc.publish(
            message={
                "wallet": {
                    "action": "reserve_wallet",
                    "body": {
                        "data": last_data
                    }
                }
            },
            headers={'wallet': True}
        ).get("wallet", {})

        if wallet_response.get("success"):
            response.status_code = wallet_response.get("status_code", 200)
            return wallet_response
        elif not wallet_response.get("success"):
            response.status_code = wallet_response.get("status_code", 417)
            return wallet_response
        raise HTTPException(status_code=wallet_response.get("status_code", 500),
                            detail={"error": wallet_response.get("error", "Wallet service Internal error")})


@app.put("/result-checkout-to-wallet", tags=["customer side"])
def result_checkout_to_wallet(response: Response,
                              order_data: ResultOrder,
                              auth_header=Depends(auth.check_current_user_tokens)
                              ):
    sub_data, token_data = auth_header
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:

        # send refresh and access token to front in header
        response.headers["accessToken"] = token_data.get("access_token")
        response.headers["refreshToken"] = token_data.get("refresh_token")
        rpc.response_len_setter(response_len=1)

        last_data = dict(order_data)
        last_data["customer_id"] = sub_data["user_id"]

        wallet_response = rpc.publish(
            message={
                "wallet": {
                    "action": "result_checkout_to_wallet",
                    "body": {
                        "data": last_data
                    }
                }
            },
            headers={'wallet': True}
        ).get("wallet", {})

        if wallet_response.get("success"):
            response.status_code = wallet_response.get("status_code", 200)
            return wallet_response
        elif not wallet_response.get("success"):
            response.status_code = wallet_response.get("status_code", 417)
            return wallet_response
        raise HTTPException(status_code=wallet_response.get("status_code", 500),
                            detail={"error": wallet_response.get("error", "Wallet service Internal error")})


@app.post("/complete-order-wallet", tags=["customer side"])
def use_complete_order_from_wallet(response: Response,
                                   order_data: CompleteOrderWallet,
                                   auth_header=Depends(auth.check_current_user_tokens)
                                   ):
    sub_data, token_data = auth_header
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:

        # send refresh and access token to front in header
        response.headers["accessToken"] = token_data.get("access_token")
        response.headers["refreshToken"] = token_data.get("refresh_token")
        rpc.response_len_setter(response_len=1)

        last_data = dict(order_data)
        last_data["customer_id"] = sub_data["user_id"]

        wallet_response = rpc.publish(
            message={
                "wallet": {
                    "action": "use_complete_order_from_wallet",
                    "body": {
                        "data": last_data
                    }
                }
            },
            headers={'wallet': True}
        ).get("wallet", {})

        if wallet_response.get("success"):
            response.status_code = wallet_response.get("status_code", 200)
            return wallet_response
        elif not wallet_response.get("success"):
            response.status_code = wallet_response.get("status_code", 417)
            return wallet_response
        raise HTTPException(status_code=wallet_response.get("status_code", 500),
                            detail={"error": wallet_response.get("error", "Wallet service Internal error")})

# ----------------------------------- end customer endpoints --------------------------------------- #
