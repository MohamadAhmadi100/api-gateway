from source.routers.order.helpers.final_helper import handle_order_bank_callback
from source.routers.wallet.wallet_modules.wallet_callback import callback_payment
from source.message_broker.rabbit_server import RabbitRPC
from fastapi import HTTPException, Response
import requests
import json


callback_service_handler = {
    "wallet": callback_payment,
    "order": handle_order_bank_callback
}


def closing_tab_handling():
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        tab_result = rpc.publish(
            message={
                "payment": {
                    "action": "check_closing_tabs",
                    "body": {}
                }
            },
            headers={'payment': True}
        )
        tab_result = tab_result.get("payment", {})
        if not tab_result.get("success"):
            raise HTTPException(status_code=tab_result.get("status_code", 500),
                                detail={"error": tab_result.get("error", "Something went wrong")})
        if len(tab_result.get("message")) > 0:
            for result in tab_result.get("message"):
                service_name = result.get("service", {})
                if service_name == "offline":
                    del result.get("message")["service"], result.get("message")["return_bank"]
                    data = requests.put(
                        "http://devob.aasood.com/offline/update_status/",
                        data=json.dumps(result.get("message", {}))
                    )
                    service_data = {"offline": {
                        "success": data.json().get("type"),
                        "message": data.json().get("message"),
                        "status_code": data.status_code
                    }}
                    return service_data
                else:
                    service_data = callback_service_handler.get(
                        service_name
                    )(
                        result=result,
                        response=Response
                    )
                final_result = service_data.get(service_name)
                if not final_result.get("success"):
                    raise HTTPException(status_code=final_result.get("status_code", 500),
                                        detail={"error": final_result.get("error", "Something went wrong")})
                return final_result.get("message")
