from fastapi import HTTPException
from starlette.exceptions import HTTPException

from source.routers.wallet.app import reserve_wallet, use_complete_order_from_wallet


def wallet_final_consume(create_order, cart, auth_header, response):
    data_reserve_wallet = {
        "amount": cart['payment'].get("walletAmount"),
        "orderNumber": create_order['orderNumber'],
        "ActionType": "auto",
        "balance": "consume"
    }
    if create_order['totalPrice'] > 0:
        data_reserve_wallet['type'] = "order"
        wallet_response = reserve_wallet(data=data_reserve_wallet, response=response,
                                         auth_header=auth_header)
        if not wallet_response.get("success"):
            raise HTTPException(status_code=wallet_response.get("status_code", 500),
                                detail={"error": "wallet not response"})

    elif create_order['totalPrice'] == 0:
        data_reserve_wallet['status'] = "complete"
        wallet_response = use_complete_order_from_wallet(data=data_reserve_wallet, response=response,
                                                         auth_header=auth_header)
        if not wallet_response.get("success"):
            raise HTTPException(status_code=wallet_response.get("status_code", 500),
                                detail={"error": "wallet not response"})
