from fastapi import HTTPException, Response, APIRouter, Depends
from source.message_broker.rabbit_server import RabbitRPC
from source.routers.customer.module.auth import AuthHandler
from source.routers.payment.validators.payment import Payment
import source.services.payment.payment_controller as payment_controller
import source.services.kosar.payment_controller as kosar_controller
import source.services.payment.bank_controller as bank_controller


router = APIRouter()
auth_handler = AuthHandler()

@router.post("/add_to_kosar", tags=["payment"])
def add_transaction_to_kosar(
        data: Payment,
        response: Response,
        auth_header=Depends(auth_handler.check_current_user_tokens)
):
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        payment_result = rpc.publish(
            message=
            payment_controller.get_info_payment(
                data=dict(data),
                bank_name=data.bank_name,
                payment_type=data.payment_type
            )
            ,
            headers={"payment": True}
        ).get("payment", {})
        if not payment_result.get("success"):
            raise HTTPException(status_code=payment_result.get("status_code", 500),
                                detail={"error": payment_result.get("error", "Something went wrong")})
        kowsar_result = rpc.publish(
            message=
            kosar_controller.kowsar_transaction(
                order_id=str(data.service_id),
                price=data.amount,
                customer_id=data.customer_id,
                bank_code=data.bank_code,
                bank_name=data.bank_name
            )
            ,
            headers={"kosar": True}
        ).get("kosar", {})
        if not kowsar_result.get("success"):
            raise HTTPException(status_code=kowsar_result.get("status_code", 500),
                                detail={"error": kowsar_result.get("error", "Something went wrong")})
        kowsar_status_result = rpc.publish(
            message=
            bank_controller.change_kowsar_status(
                kowsar_status=kowsar_result.get("message"),
                payment_id=payment_result.get("message", {}).get("pay_id")
            ),
            headers={"payment": True}
        ).get("payment", {})
        if not kowsar_status_result.get("success"):
            raise HTTPException(status_code=kowsar_status_result.get("status_code", 500),
                                detail={"error": kowsar_status_result.get("error", "Something went wrong")})
        order_result = rpc.publish(
            message=
            {
                "order": {
                    "action": "kosar_response_order",
                    "body": {
                        "kosar_detail": {
                            "success": True if kowsar_result.get("message", {}) == "successful" else False,
                            "kosarDate": kowsar_result.get("date")
                        },
                        "order_id": data.service_id,
                        "kosar_type": "transaction"
                    }
                }
            }
            ,
            headers={"order": True}
        ).get("order", {})
        if not order_result.get("success"):
            raise HTTPException(status_code=order_result.get("status_code", 500),
                                detail={"error": order_result.get("error", "Something went wrong")})
        response.status_code = order_result.get("status_code")
        return order_result.get("message")