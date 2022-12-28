from starlette.responses import RedirectResponse

from source.message_broker.rabbit_server import RabbitRPC
from fastapi import HTTPException, Response


def callback_payment(result, response: Response):
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        service_data = rpc.publish(
            message={
                "wallet":
                    {
                        "action": "charge_wallet",
                        "body": {
                            "data": result
                        }
                    }
            },
            headers={"wallet": True}
        ).get("wallet", {})
        # customer_type = service_data.get('message', {}).get('customer_type')
        # if customer_type == "B2B":
        return RedirectResponse(
            f"https://aasood.com/payment-result/wallet/{service_data.get('message', {}).get('service_id')}")
        # return RedirectResponse(
        #     f"https://rakiano.com/payment-result/wallet/{service_data.get('message', {}).get('service_id')}")
