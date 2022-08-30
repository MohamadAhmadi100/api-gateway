import json
from typing import Optional, List
from fastapi import HTTPException, Response, Query, APIRouter
from source.helpers.case_converter import convert_case
from source.message_broker.rabbit_server import RabbitRPC
from source.routers.order.helpers.final_helper import handle_order_bank_callback
import requests
from source.routers.wallet.wallet_modules.wallet_callback import callback_payment
from source.routers.payment.validators.kowsar import DateSort
# from source.helpers.rabbit_config import new_rpc
import source.services.payment.payment_controller as payment_controller
import source.services.kosar.payment_controller as kosar_controller
import source.services.payment.bank_controller as bank_controller
import source.services.customer.router_back_office as customer_controller

callback_service_handler = {
    "wallet": callback_payment,
    "order": handle_order_bank_callback
}

router = APIRouter()


@router.get("/get_payment_transaction/")
def get_payment(
        response: Response,
        page: Optional[int] = Query(1),
        per_page: Optional[int] = Query(15),
        banks: Optional[list] = Query(None),
        price_from: Optional[int] = Query(None),
        price_to: Optional[int] = Query(None),
        date_from: Optional[str] = Query(None),
        date_to: Optional[str] = Query(None),
        date_sort: DateSort = Query(default=DateSort.DESC),
        status: Optional[List[str]] = Query(None),
        kowsar_status: Optional[list] = Query(None),
        search: Optional[str] = Query(None)
):
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        if search and search.isalpha():
            rpc.response_len_setter(response_len=1)
            customer_result = rpc.publish(
                message={
                    "customer": {
                        "action": "search_customers_by_name",
                        "body": {
                            "phrase": search
                        }
                    }
                },
                headers={'customer': True}
            )
            customer_result = customer_result.get("customer", {})
            if not customer_result.get("success"):
                raise HTTPException(status_code=customer_result.get("status_code", 500),
                                    detail={"error": customer_result.get("error", "Something went wrong")})
            search = {"customer_id": customer_result.get("message")}
        else:
            search = {"service_id": search, "payment_id": search}
        payment_result = rpc.publish(
            message=
            payment_controller.get_payment(
                page=page,
                per_page=per_page,
                filters={
                    "date": [date_from, date_to] if date_to or date_from else None,
                    "banks": banks,
                    "amount": [price_from, price_to] if price_to or price_from else None,
                    "send_status": status,
                    "date_sort": date_sort.value,
                    "kowsar_status": kowsar_status,
                    **search
                }
            ),
            headers={"payment": True}
        ).get("payment", {})
        if not payment_result.get("success"):
            raise HTTPException(status_code=payment_result.get("status_code", 500),
                                detail={"error": payment_result.get("error", "Something went wrong")})
        status_code = payment_result.get("status_code")
        payment_result = payment_result.get("message", {})
        if not payment_result.get("transaction"):
            del payment_result["customer_id_list"]
            response.status_code = status_code
            return payment_result
        final_result = rpc.publish(
            message=
            customer_controller.get_customer_data_by_id(
                id_list=list(set(payment_result.get("customer_id_list")))
            ),
            headers={"customer": True}
        ).get("customer", {})
        if not final_result.get("success"):
            raise HTTPException(status_code=final_result.get("status_code", 500),
                                detail={"error": final_result.get("error", "Something went wrong")})
        response.status_code = final_result.get("status_code")
        final_result = convert_case(final_result.get("message"), "camel")
        for result in payment_result.get("transaction"):
            customer_result = final_result.get(str(result.get("customerId")))
            if customer_result is None:
                customer_result = {'firstName': None, 'lastName': None, 'kowsarNumber': None}
            result.update(customer_result)
        del payment_result["customer_id_list"]
        return payment_result


@router.put("/change_kowsar_status/")
def change_kowsar_status(
        service_id: str,
        response: Response
):
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        check_order_result = rpc.publish(
            message=
            payment_controller.get_payment_by_service_id(
                service_id=service_id
            ),
            headers={"payment": True}
        ).get("payment", {})
        if not check_order_result.get("success"):
            raise HTTPException(status_code=check_order_result.get("status_code", 500),
                                detail={"error": check_order_result.get("error", "Something went wrong")})
        check_order_result = check_order_result.get("message")
        kowsar_result = rpc.publish(
            message=
            kosar_controller.kowsar_transaction(
                order_id=service_id,
                price=check_order_result.get("amount"),
                customer_id=check_order_result.get("customer_id"),
                bank_code=check_order_result.get("bank_code"),
                bank_name=check_order_result.get("bank_name")
            ),
            headers={"kosar": True}
        ).get("kosar", {})
        if not kowsar_result.get("success"):
            raise HTTPException(status_code=kowsar_result.get("status_code", 500),
                                detail={"error": kowsar_result.get("error", "Something went wrong")})
        kowsar_status_result = rpc.publish(
            message=
            bank_controller.change_kowsar_status(
                kowsar_status=kowsar_result.get("message"),
                payment_id=check_order_result.get("payment_id")
            ),
            headers={"payment": True}
        ).get("payment", {})
        result = kowsar_status_result.get("message")
        #     service_name = result.get("service", {})
        #     if service_name == "offline":
        #         del result["service"]
        #         data = requests.put(
        #             "http://devob.aasood.com/offline/update_status/",
        #             data=json.dumps(result)
        #         )
        #         service_data = {"offline": {
        #             "success": data.json().get("type"),
        #             "message": data.json().get("message"),
        #             "status_code": data.status_code
        #         }}
        #     else:
        #         service_data = callback_service_handler.get(
        #             service_name
        #         )(
        #             result=result,
        #             response=response
        #         )
        # except:
        #     ...
        response.status_code = kowsar_result.get("status_code")
        return kowsar_result.get("message")
