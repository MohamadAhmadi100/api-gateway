import json
import logging
import random
from fastapi.responses import RedirectResponse
from fastapi import HTTPException, Response, APIRouter, Request, Body, Query

from source.helpers.case_converter import convert_case
# from source.helpers.rabbit_config import new_rpc
from source.message_broker.rabbit_server import RabbitRPC
from source.routers.dealership.controllers.payment_callback import dealership_bank_callback
from source.routers.order.helpers.final_helper import handle_order_bank_callback
import requests
from source.routers.payment.modules import payment_modules
from source.routers.payment.validators import payment
from source.routers.wallet.wallet_modules.wallet_callback import callback_payment
import source.services.payment.bank_controller as bank_controller
import source.services.uis.uis_controller as uis_controller
import source.services.kosar.payment_controller as kosar_controller

callback_service_handler = {
    "wallet": callback_payment,
    "order": handle_order_bank_callback,
    "dealership": dealership_bank_callback
}

BANK_NAMES = ["mellat", "saman"]

router = APIRouter()


@router.post("/send_data")
def get_url(data: payment.SendData, response: Response):
    bank_name = "saman" if data.amount > 1_000_000_000 else random.choice(BANK_NAMES)
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        payment_result = rpc.publish(
            message=
            bank_controller.get_data(
                data=dict(data),
                bank_name=bank_name
            )
            ,
            headers={"payment": True}
        )
        payment_result = payment_result.get("payment", {})
        if not payment_result.get("success"):
            return {
                "error": payment_result.get("error", "Something went wrong"),
                "success": False,
                "status_code": payment_result.get("status_code", 500)
            }

        token_result = payment_modules.request_bank_handler(
            api=payment_result.get("message", {}).get("url"),
            data=payment_result.get("message", {}).get("bank_data"),
            bank_name=payment_result.get("message", {}).get("bank_name")
        )
        url_result = rpc.publish(
            message=
            bank_controller.redirect_url(
                data=token_result,
                payment_id=payment_result.get("message", {}).get("payment_id"),
                bank_name=payment_result.get("message", {}).get("bank_name")
            ),
            headers={"payment": True}
        )
        url_result = url_result.get("payment", {})
        if not url_result.get("success"):
            return {
                "error": url_result.get("error", "Something went wrong"),
                "success": False,
                "status_code": url_result.get("status_code", 500)
            }

        uis_result = rpc.publish(
            message=
            uis_controller.hashed_generator(
                link=url_result.get("message")
            ),
            headers={"uis": True}
        )
        uis_result = uis_result.get("uis", {})
        response.status_code = uis_result.get("status_code")
        return uis_result


@router.post("/callback")
async def set_callback(request: Request, response: Response):
    response_string: bytes = await request.body()
    response_string: str = response_string.decode("utf-8")
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        result = rpc.publish(
            message=
            bank_controller.callback_pay(
                request=response_string
            ),
            headers={"payment": True}
        )
        result = result.get("payment", {})
        if result.get("success"):
            verify_result = payment_modules.request_bank_handler(
                api=result.get("message", {}).get("url"),
                data=result.get("message", {}).get("bank_data"),
                bank_name=result.get("message", {}).get("bank_name")
            )
            del result.get("message")["url"], result.get("message")["bank_data"]
            result["message"].update(**{"verify_log": verify_result})
            check_verify_res = rpc.publish(
                message=
                bank_controller.check_verify(
                    data=result.get("message", {}).get("verify_log"),
                    token=result.get("message", {}).get("token"),
                    bank_name=result.get("message", {}).get("bank_name")
                ),
                headers={"payment": True}
            ).get("payment", {})
            if not check_verify_res.get("message", {}):
                verify_data = check_verify_res.get("data")
                result["message"].update(verify_data)
                result["message"]["status"] = "پرداخت موفقیت آمیز بود و اعتبارسنجی" \
                                              " با موفقیت انجام شد" \
                                              " اما با خطای مانگو مواجه هستیم"
            else:
                result = check_verify_res
        if result.get("message", {}).get("is_paid") and result.get("success"):
            kowsar_result = rpc.publish(
                message=
                kosar_controller.kowsar_transaction(
                    order_id=result.get("message", {}).get("service_id"),
                    price=result.get("message", {}).get("amount"),
                    customer_id=result.get("message", {}).get("customer_id"),
                    bank_code=result.get("message", {}).get("bank_code"),
                    bank_name=result.get("message", {}).get("bank_name")
                )
                ,
                headers={"kosar": True}
            )
            kowsar_result = kowsar_result.get("kosar", {})
            kowsar_status_result = rpc.publish(
                message=
                bank_controller.change_kowsar_status(
                    kowsar_status=kowsar_result.get("message"),
                    payment_id=result.get("message", {}).get("payment_id")
                ),
                headers={"payment": True}
            )
            kowsar_status_result = kowsar_status_result.get("payment", {})
            result = kowsar_status_result

        service_name = result.get("message", {}).get("service", {})
        if service_name == "offline":
            del result.get("message")["service"], result.get("message")["return_bank"]
            data = requests.put(
                "http://devob.aasood.com/offline/update_status/",
                data=json.dumps(result.get("message", {}))
            )
            service_data = {
                "success": data.json().get("type"),
                "message": data.json().get("message"),
                "status_code": data.status_code
            }
        else:
            service_data = callback_service_handler.get(
                service_name
            )(
                result=result.get("message", {}),
                response=response
            )
            # if service_name == "wallet":
            #     result = 3 if service_data.get("result") else 4
            # elif service_name == "order":
            #     result = 1 if service_data.get("result") else 2
            # return RedirectResponse(
            #     f"https://aasood.com/payment-result/{result}/{service_data.get('service_id')}")


@router.post("/closed_tabs", include_in_schema=False)
def closing_tab_handling(data: list = Body(...)):
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        for result in data:
            service_name = result.get("service", {})
            try:
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
                else:
                    service_data = callback_service_handler.get(
                        service_name
                    )(
                        result=result,
                        response=Response
                    )
            except Exception as e:
                logging.error(e)
                continue


@router.post("/cancel_pending")
def cancel_pending_payment(
        service_id: str = Query(..., alias="serviceId")
):
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        cancel_result = rpc.publish(
            message=bank_controller.cancel_pending_payment(service_id=service_id),
            headers={"payment": True}
        ).get("payment", {})
        if not cancel_result.get("success"):
            raise HTTPException(status_code=cancel_result.get("status_code", 500),
                                detail={"error": cancel_result.get("error", "Something went wrong")})
        cancel_result = cancel_result.get("message")
        service_name = cancel_result.get("service", {})
        if service_name == "offline":
            del cancel_result.get("message")["service"], cancel_result.get("message")["return_bank"]
            data = requests.put(
                "http://devob.aasood.com/offline/update_status/",
                data=json.dumps(cancel_result.get("message", {}))
            )
            service_data = {"offline": {
                "success": data.json().get("type"),
                "message": data.json().get("message"),
                "status_code": data.status_code
            }}
        else:
            service_data = callback_service_handler.get(
                service_name
            )(
                result=cancel_result,
                response=Response
            )
        return "completed"


@router.get("/re_redirect")
def get_the_url_again(
        response: Response,
        service_id: str = Query(..., alias="serviceId"),
):
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        url_result = rpc.publish(
            message=bank_controller.create_url_again(service_id=service_id),
            headers={"payment": True}
        ).get("payment", {})
        if not url_result.get("success"):
            raise HTTPException(status_code=url_result.get("status_code", 500),
                                detail={"error": url_result.get("error", "Something went wrong")})
        response.status_code = url_result.get("status_code")
        return convert_case(url_result.get("message"), "camel")


@router.get("/payment_result")
def get_bank_result(
        response: Response,
        service_name: str = Query(..., alias="serviceName"),
        service_id: str = Query(..., alias="serviceId")
):
    service_handlers = {
        "order": "response_order_call_back",
        "wallet": "get_transaction_by_service_id"
    }
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        payment_result = rpc.publish(
            message={
                service_name: {
                    "action": service_handlers.get(service_name),
                    "body": {
                        "service_id": service_id,
                    }
                }
            },
            headers={service_name: True}
        ).get(service_name, {})
        if not payment_result.get("success"):
            raise HTTPException(status_code=payment_result.get("status_code", 500),
                                detail={"error": payment_result.get("error", "Something went wrong")})
        response.status_code = payment_result.get("status_code")
        return {
            "payment": payment_result.get("payment"),
            "message": payment_result.get("message"),
            "device_type": payment_result.get("device_type")}
