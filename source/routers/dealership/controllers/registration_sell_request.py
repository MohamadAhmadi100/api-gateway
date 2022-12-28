from fastapi import Depends, APIRouter, Response

from source.helpers.case_converter import convert_case
from source.message_broker.rabbit_server import RabbitRPC
from source.routers.customer.helpers.profile_view import get_profile_info
from source.routers.customer.module.auth import AuthHandler
from source.routers.dealership.validators.register_sell_request import SellRequest
from source.routers.uis.app import create_link
from source.routers.uis.validators.uis import Uis

router = APIRouter()
auth_handler = AuthHandler()


@router.post("/create_sell_request", tags=["register forms"])
def sell_request(data: SellRequest,
                 response: Response,
                 auth_header=Depends(auth_handler.check_current_user_tokens)):
    user, token = auth_header
    payment_type = data.dict().get("payment_type")
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        dealership_response = rpc.publish(
            message={
                "dealership": {
                    "action": "calculate_wage",
                    "body": {
                        "products": data.dict().get("products"),
                    }
                }
            },
            headers={'dealership': True}
        ).get("dealership", {})
        if dealership_response.get("success"):
            rpc.response_len_setter(response_len=1)
            order_response = rpc.publish(
                message={
                    "order": {
                        "action": "place_order_delaership",
                        "body": {
                            "dealership_detail": {
                                "dealershipId": user.get("user_id"),
                                "dealershipPhoneNumber": user.get("phone_number")
                            },
                            "customer_detail": get_profile_info(data.dict().get("customer")),
                            "products": data.dict().get("products"),
                            "device_type": data.dict().get("device_type"),
                            "wage": dealership_response.get("wage"),
                            "payment_type": payment_type
                        }
                    }
                },
                headers={'order': True}
            ).get("order", {})
            if order_response.get("success") and payment_type == "aiBanking":
                uis = Uis(
                    requestType="dealership",
                    serviceData={"amount": order_response.get("bank_response").get("amount") * 10,
                                 "customerId": order_response.get("bank_response").get("customerId"),
                                 "serviceName": order_response.get("bank_response").get("serviceName"),
                                 "serviceId": order_response.get("bank_response").get("serviceId"),
                                 },
                    userList=[
                        {
                            "phone_number": order_response.get("order_object").get("customer").get("mobile"),
                            "full_name": order_response.get("order_object").get("customer").get("fullName")
                        }
                    ],
                    sendMethodList=[
                        "sms"
                    ],
                    customerId=order_response.get("bank_response").get("customerId")
                )
                uis = convert_case(uis, "snake")
                uis_response = create_link(
                    data=uis,
                    response=response
                )
                return uis_response


            elif order_response.get("success") and payment_type == "cashondelivery":
                return order_response
            return order_response
        return dealership_response
# {
#   "customer": {
#     "customerId": "20025",
#     "customerPhoneNumber": "09355055825"
#   },
#   "products": [
#     {
#       "status": "initial",
#       "systemCode": "2000010010001001001001001",
#       "storageId": "1",
#       "price": 618000,
#       "totalPrice": 618000,
#       "count": 1,
#       "model": "A01 Core",
#       "name": "Mobile Samsung A01 Core (1GB 16GB 4G) Vietnam",
#       "brand": {
#         "value": "Samsung",
#         "label": "Samsung"
#     },
#       "color": {
#         "value": "white",
#         "label": "white"
#     },
#       "guarantee": {
#         "value": "Aawaat",
#         "label": "Aawaat"
#     },
#       "seller": {
#         "value": "ASD",
#         "label": "ASD"
#     },
#       "category": {
#         "value": "ASD",
#         "label": "موبایل"
#     },
#       "imeis": [
#         "111"
#       ]
#     }
#   ]
# }
