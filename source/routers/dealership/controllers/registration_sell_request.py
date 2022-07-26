from fastapi import Depends, APIRouter
from source.message_broker.rabbit_server import RabbitRPC
from source.routers.customer.module.auth import AuthHandler
from source.routers.dealership.validators.register_sell_request import SellRequest

router = APIRouter()
auth_handler = AuthHandler()



@router.post("/create_sell_request", tags=["Sell request for end user"])
def sell_request(data: SellRequest,
                 auth_header=Depends(auth_handler.check_current_user_tokens)):
    user, token = auth_header
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        sell_request_response = rpc.publish(
            message={
                "dealership": {
                    "action": "insert_sell_request",
                    "body": {
                        "customer_id": user.get("user_id"),
                        "data": data.dict()
                    }
                }
            },
            headers={'dealership': True}
        ).get("dealership", {})
        if sell_request_response.get("success"):
            return sell_request_response
            # rpc.response_len_setter(response_len=1)
            # add_imei_response = rpc.publish(
            #     message={
            #         "dealership": {
            #             "action": "add_imei",
            #             "body": {
            #                 "data": data.dict()
            #             }
            #         }
            #     },
            #     headers={'dealership': True}
            # ).get("dealership", {})
            # if add_imei_response.get("success"):
            #     return add_imei_response
            # return add_imei_response
        return sell_request_response