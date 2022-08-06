import json
import random
from fastapi.responses import RedirectResponse
from fastapi import HTTPException, Response, APIRouter, Request
from source.helpers.rabbit_config import new_rpc
# from source.message_broker.rabbit_server import RabbitRPC
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
    "order": handle_order_bank_callback
}

BANK_NAMES = ["mellat"]

router = APIRouter()


@router.post("/send_data")
def get_url(data: payment.SendData, response: Response):
    bank_name = random.choice(BANK_NAMES)
    payment_result = new_rpc.publish(
        message=[
            bank_controller.get_data(
                data=dict(data),
                bank_name=bank_name
            )
        ]
    )
    if not payment_result.get("success"):
        raise HTTPException(status_code=payment_result.get("status_code", 500),
                            detail={"error": payment_result.get("error", "Something went wrong")})

    token_result = payment_modules.request_bank_handler(
        api=payment_result.get("message", {}).get("url"),
        data=payment_result.get("message", {}).get("bank_data"),
        bank_name=payment_result.get("message", {}).get("bank_name")
    )
    url_result = new_rpc.publish(
        message=[
            bank_controller.redirect_url(
                data=token_result,
                payment_id=payment_result.get("message", {}).get("payment_id"),
                bank_name=payment_result.get("message", {}).get("bank_name")
            )
        ]
    )
    if not url_result.get("success"):
        raise HTTPException(status_code=url_result.get("status_code", 500),
                            detail={"error": url_result.get("error", "Something went wrong")})

    uis_result = new_rpc.publish(
        message=[
            uis_controller.hashed_generator(
                link=url_result.get("message")
            )
        ]
    )
    response.status_code = uis_result.get("status_code")
    return uis_result


@router.post("/callback")
async def set_callback(response_string: str, response: Response):
    # response_string: bytes = await request.body()
    # response_string: str = response_string.decode("utf-8")
    result = new_rpc.publish(
        message=[
            bank_controller.callback_pay(
                request=response_string
            )
        ]
    )
    if result.get("success"):
        verify_result = payment_modules.request_bank_handler(
            api=result.get("message", {}).get("url"),
            data=result.get("message", {}).get("bank_data"),
            bank_name=result.get("message", {}).get("bank_name")
        )
        if verify_result.get("response"):
            verify_log = {"verify_log": verify_result.get("message")}
            del result.get("message")["url"], result.get("message")["bank_data"]
            verify_result["message"] = {**verify_log, **result.get("message")}
            result = verify_result
            check_verify_res = new_rpc.publish(
                message=[
                    bank_controller.check_verify(
                        data=result.get("message", {}).get("verify_log"),
                        token=result.get("message", {}).get("token"),
                        bank_name=result.get("message", {}).get("bank_name")
                    )
                ]
            )
            if not check_verify_res.get("message", {}):
                verify_data = check_verify_res.get("data")
                result["message"].update(verify_data)
                result["message"]["status"] = "پرداخت موفقیت آمیز بود و اعتبارسنجی" \
                                              " با موفقیت انجام شد" \
                                              " اما با خطای مانگو مواجه هستیم"
            else:
                result = check_verify_res
    # if result.get("message", {}).get("is_paid") and result.get("success"):
    #     kowsar_result = new_rpc.publish(
    #         message=[
    #             kosar_controller.kowsar_transaction(
    #                 order_id=result.get("message", {}).get("order_id"),
    #                 price=result.get("message", {}).get("amount"),
    #                 customer_id=result.get("message", {}).get("customer_id"),
    #                 bank_code=result.get("message", {}).get("bank_code"),
    #                 bank_name=result.get("message", {}).get("bank_name")
    #             )
    #         ]
    #     )
    #     kowsar_status_result = new_rpc.publish(
    #         message=[
    #             bank_controller.change_kowsar_status(
    #                 kowsar_status=kowsar_result,
    #                 payment_id=result.get("message", {}).get("payment_id")
    #             )
    #         ]
    #     )
    #     result = kowsar_status_result

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
        if service_name == "wallet":
            result = 3 if service_data.get("result") else 4
        elif service_name == "order":
            result = 1 if service_data.get("result") else 2
        return RedirectResponse(
            f"https://m.aasood.ir/payment-result/{result}/{service_data.get('service_id')}")
