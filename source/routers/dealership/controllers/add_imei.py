from fastapi import Depends, APIRouter
from source.message_broker.rabbit_server import RabbitRPC
from source.routers.customer.module.auth import AuthHandler
from source.routers.dealership.validators.insert_imei import IMEI


router = APIRouter()
auth_handler = AuthHandler()



@router.post("/add_imei", tags=["warehouse"])
def add_imei(data: IMEI):
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        check_imei_response = rpc.publish(
            message={
                "dealership": {
                    "action": "check_repetitious_imei",
                    "body": {
                        "data": data.dict()
                    }
                }
            },
            headers={'dealership': True}
        ).get("dealership", {})
        if check_imei_response.get("success"):
            rpc.response_len_setter(response_len=1)
            add_imei_response = rpc.publish(
                message={
                    "dealership": {
                        "action": "add_imei",
                        "body": {
                            "data": data.dict()
                        }
                    }
                },
                headers={'dealership': True}
            ).get("dealership", {})
            if add_imei_response.get("success"):
                return add_imei_response
            return add_imei_response
        return check_imei_response
