"""
* this rout is for wallet that have two branch(back office side/ customer side)
* in this rout all of customers data get in token
* all of api objects first validated in "validators" directory then send to services
"""
from fastapi import FastAPI, HTTPException, Response, responses, Depends
from starlette.exceptions import HTTPException as starletteHTTPException
from source.config import settings
from source.message_broker.rabbit_server import RabbitRPC
from source.routers.wallet.validators.transaction import Transaction
from source.routers.wallet.validators.update_wallet import UpdateData
from source.routers.customer.module.auth import AuthHandler
from source.routers.wallet.validators.checkout_wallet import Reserve, ResultOrder, CompleteOrderWallet
from source.routers.wallet.validators.charge_wallet import Charge
from source.routers.payment.validators.payment import SendData
from source.helpers.case_converter import convert_case
from source.routers.payment.app import get_url

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


@app.put("/update-wallet", tags=["customer side"])
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


@app.post("/get-transactions", tags=["customer side"])
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


@app.get("/get-customer-wallet", tags=["customer side"])
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


@app.put("/result-checkout", tags=["customer side"])
def result_checkout(response: Response,
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
                    "action": "result_checkout",
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
def complete_order_wallet(response: Response,
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
                    "action": "complete_order_wallet",
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


@app.put("/charge-wallet", tags=["customer side"])
def charge_wallet(
        charge_data: Charge,
        response: Response,
        auth_header=Depends(auth.check_current_user_tokens)
):
    sub_data, token_data = auth_header
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        response.headers["accessToken"] = token_data.get("access_token")
        response.headers["refreshToken"] = token_data.get("refresh_token")
        rpc.response_len_setter(response_len=1)
        wallet_response = rpc.publish(
            message={
                "wallet": {
                    "action": "create_transaction",
                    "body": {
                        "data": {
                            "customer_id": sub_data["user_id"],
                            "amount": charge_data.amount,
                            "payment_method": "online",
                            "balance": "charge",
                            "wallet_id": charge_data.wallet_id,
                            "type": "chargeWallet",
                            "action_type": "auto"
                        }
                    }
                },
            },
            headers={'wallet': True}
        ).get("wallet", {})

        if wallet_response.get("success"):
            transaction = wallet_response.get("message")
        send_data = SendData(
            amount=charge_data.amount,
            customerId=charge_data.customer_id,
            serviceName="wallet",
            serviceId=transaction.get("transactionId"),
            bankName=charge_data.bank_name
        )
        send_data = convert_case(send_data, "snake")
        payment_result = get_url(
            data=send_data,
            response=Response
        )
        return payment_result
