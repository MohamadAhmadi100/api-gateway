from fastapi import FastAPI, HTTPException, Response, responses, Depends
from starlette.exceptions import HTTPException as starletteHTTPException
from source.config import settings
from source.message_broker.rabbit_server import RabbitRPC
from source.routers.wallet.validators.transaction import Transaction
from source.routers.wallet.validators.wallets import Wallet
from source.routers.wallet.validators.update_wallet import UpdateData
from source.routers.customer.module.auth import AuthHandler
from source.routers.wallet.validators.charge_wallet import Charge
from source.routers.payment.modules import payment_modules
from source.routers.wallet.validators.checkout_wallet import Reserve, Order, OrderWallet, CancelOrder,ChargeWallet

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


# --------------------------------- start back-office endpoints -------------------------------------- #
@app.post("/create-wallet", tags=["back-office side"])
def create_wallet(response: Response,
                  auth_header=Depends(auth.check_current_user_tokens)
                  ):
    """
    Creating a wallet after the customer approved by the staffs
    """
    sub_data, token_data = auth_header
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        result = rpc.publish(
            message={
                "customer": {
                    "action": "get_profile",
                    "body": {
                        "customer_phone_number": sub_data,
                    }
                }
            },
            headers={'customer': True}
        )
    customer_result = result.get("customer", {})
    if not customer_result.get("success"):
        raise HTTPException(
            status_code=customer_result.get("status_code", 500),
            detail={"error": customer_result.get("error", "Something went wrong")}
        )
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:

        # send refresh and access token to front in header
        response.headers["accessToken"] = token_data.get("access_token")
        response.headers["refreshToken"] = token_data.get("refresh_token")
        rpc.response_len_setter(response_len=1)

        # get customer data from token and send that for create wallet
        data = {
            "customer_id": sub_data.get("user_id"),
            "phone_number": sub_data.get("phone_number"),
            "customer_name": customer_result["message"]["customerFirstName"] + " " + customer_result["message"][
                "customerLastName"]

        }

        wallet_response = rpc.publish(
            message={
                "wallet": {
                    "action": "create_wallet",
                    "body": {
                        "data": data
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


@app.get("/customer-wallet-back", tags=["back-office side"])
def get_customer_wallet_back_side(response: Response,
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
                    "action": "get_customer_wallet_back_side",
                    "body": {
                        "data": int(sub_data.get("user_id"))
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


@app.post("/get-wallets", tags=["back-office side"])
def get_wallets(response: Response, data: Wallet,
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
                    "action": "get_wallets",
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
        elif not wallet_response.get("success"):
            response.status_code = wallet_response.get("status_code", 417)
            return wallet_response
        raise HTTPException(status_code=wallet_response.get("status_code", 500),
                            detail={"error": wallet_response.get("error", "Wallet service Internal error")})


@app.put("/update_wallet", tags=["back-office side"])
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


@app.post("/transactions", tags=["back-office side"])
def get_transactions(response: Response, data: Transaction,
                     auth_header=Depends(auth.check_current_user_tokens)
                     ):
    """
    use of post method for get transaction datas
    in this api staff could get transaction data by filters/range data/search/sort and pagination
    """
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        sub_data, token_data = auth_header
        response.headers["accessToken"] = token_data.get("access_token")
        response.headers["refreshToken"] = token_data.get("refresh_token")
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
        elif not wallet_response.get("success"):
            response.status_code = wallet_response.get("status_code", 417)
            return wallet_response
        raise HTTPException(status_code=wallet_response.get("status_code", 500),
                            detail={"error": wallet_response.get("error", "Wallet service Internal error")})


@app.put("/change_wallet_status", tags=["back-office side"])
def change_wallet_status(response: Response,
                         auth_header=Depends(auth.check_current_user_tokens)
                         ):
    sub_data, token_data = auth_header
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:

        # send refresh and access token to front in header
        response.headers["accessToken"] = token_data.get("access_token")
        response.headers["refreshToken"] = token_data.get("refresh_token")
        rpc.response_len_setter(response_len=1)

        # get customer data from token and send that for create wallet
        data = {
            "customer_id": sub_data.get("user_id"),
        }

        wallet_response = rpc.publish(
            message={
                "wallet": {
                    "action": "change_wallet_status",
                    "body": {
                        "data": data
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


# --------------------------------- end back-office endpoints -------------------------------------- #
# ---------------------------------- start customer endpoints -------------------------------------- #


@app.post("/transaction", tags=["customer side"])
def get_transaction(response: Response, data: Transaction,
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
                    "action": "customer_get_transaction",
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
def get_customer_wallet_customer_side(
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
                    "action": "get_customer_wallet_customer_side",
                    "body": {
                        "customer_id": sub_data.get("user_id")
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


@app.put("/charge_wallet", tags=["charge wallet amount"])
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


@app.put("/order-result", tags=["customer side"])
def order_result(response: Response,
                 order_data: Order,
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
                    "action": "order_result",
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

@app.post("/order-wallet", tags=["customer side"])
def order_wallet(response: Response,
                 order_data: OrderWallet,
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
                    "action": "order_wallet",
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


@app.post("/cancel-order", tags=["customer side"])
def cancel_order(response: Response,
                 order_data: CancelOrder,
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
                    "action": "cancel_order",
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
