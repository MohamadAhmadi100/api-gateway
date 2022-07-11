from fastapi import APIRouter
from fastapi import Response, Depends

from source.message_broker.rabbit_server import RabbitRPC
from source.routers.customer.module.auth import AuthHandler

credit = APIRouter()
auth_handler = AuthHandler()


@credit.get("/create_credit/", tags=["customer_side"])
def customer_credit(response: Response,
                    auth_header=Depends(auth_handler.check_current_user_tokens)):
    user, auth = auth_header
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        order_response = rpc.publish(
            message={
                "credit": {
                    "action": "create_credit",
                    "body": {
                        "customer_id": user.get("user_id"),
                    }
                }
            },
            headers={'credit': True}
        ).get("credit", {})
        response.status_code = 200
        return order_response
