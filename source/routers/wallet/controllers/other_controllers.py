"""
* this rout is for wallet that have two branch(back office side/ customer side)
* in this rout all of customers data get in token
* all of api objects first validated in "validators" directory then send to services
"""
from source.message_broker.rabbit_server import RabbitRPC
from source.routers.wallet.validators.transaction import Transaction
from source.routers.wallet.validators.update_wallet import UpdateData
from source.routers.customer.module.auth import AuthHandler
from source.routers.wallet.validators.checkout_wallet import Reserve, ResultOrder, CompleteOrderWallet
from fastapi import HTTPException, Response, Depends, Query, APIRouter

from source.helpers.rabbit_config import new_rpc
from source.services.wallet import router_wallet as wallet_funcs

from enum import Enum
from typing import Optional

router = APIRouter()
auth = AuthHandler()


class SortType(str, Enum):
    asc = "asc"
    desc = "desc"


@router.put("/update-wallet", tags=["customer side"])
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


@router.post("/get-transactions", tags=["customer side"])
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


@router.get("/get-customer-wallet", tags=["customer side"])
def get_wallet_by_customer_id_(
        response: Response,
        auth_header=Depends(auth.check_current_user_tokens)
):
    sub_data, token_data = auth_header
    # with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
    #     response.headers["accessToken"] = token_data.get("access_token")
    #     response.headers["refreshToken"] = token_data.get("refresh_token")
    #     rpc.response_len_setter(response_len=1)
    #
    #     wallet_response = rpc.publish(
    #         message={
    #             "wallet": {
    #                 "action": "get_wallet_by_customer_id",
    #                 "body": {
    #                     "customer_id": sub_data.get("user_id")
    #                 }
    #             }
    #         },
    #         headers={'wallet': True}
    #     ).get("wallet", {})

    wallet_response = new_rpc.publish(
        message=[
            wallet_funcs.get_wallet_by_customer_id(customer_id=sub_data.get("user_id"))]
    )

    if wallet_response.get("success"):
        response.status_code = wallet_response.get("status_code", 200)
        return wallet_response
    elif not wallet_response.get("success"):
        response.status_code = wallet_response.get("status_code", 417)
        return wallet_response
    raise HTTPException(status_code=wallet_response.get("status_code", 500),
                        detail={"error": wallet_response.get("error", "Wallet service Internal error")})


@router.post("/reserve-wallet", tags=["customer side"])
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


@router.put("/result-checkout", tags=["customer side"])
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


@router.post("/complete-order-wallet", tags=["customer side"])
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


@router.get("/get-report-wallet-log", tags=["customer side"])
def get_report_wallet_log(response: Response,
                          customerId: int = Query(...),
                          page: int = None,
                          perPage: int = None,
                          sortName: str = None,
                          sortType: Optional[SortType] = None,
                          auth_header=Depends(auth.check_current_user_tokens)

                          ):
    sub_data, token_data = auth_header
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        data = {
            "customerId": customerId,
            "page": page,
            "perPage": perPage,
            "sortName": sortName,
            "sortType": sortType,

        }
        wallet_response = rpc.publish(
            message={
                "wallet": {
                    "action": "get_report_wallet_log",
                    "body": {
                        "data": data
                    }
                }
            },
            headers={'wallet': True}
        ).get("wallet", {})
        response.headers["accessToken"] = token_data.get("access_token")
        response.headers["refreshToken"] = token_data.get("refresh_token")

        if wallet_response.get("success"):
            response.status_code = wallet_response.get("status_code", 200)
            return wallet_response
        elif not wallet_response.get("success"):
            response.status_code = wallet_response.get("status_code", 417)
            return wallet_response
        raise HTTPException(status_code=wallet_response.get("status_code", 500),
                            detail={"error": wallet_response.get("error", "Wallet service Internal error")})
