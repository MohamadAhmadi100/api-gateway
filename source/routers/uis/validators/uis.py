import re
from fastapi import HTTPException

from pydantic import BaseModel, validator, Field
from source.routers.payment.validators.payment import SendData


class Uis(BaseModel):
    request_type: str = Field(..., alias="requestType")
    service_data: dict = Field(..., alias="serviceData")
    user_list: list = Field(..., alias="userList")
    send_method_list: list = Field(..., alias="sendMethodList")
    customer_id: int = Field(..., alias="customerId")

    @validator('request_type')
    def check_request_type(cls, request_type):
        request_types = ["offline", "dealership", "coupon"]
        if request_type.lower() not in request_types:
            raise HTTPException(status_code=422, detail={"error": "request_type is not acceptable!"})
        return request_type

    @validator("user_list")
    def check_user_list(cls, user_list):
        if len(user_list) == 0:
            raise HTTPException(status_code=422, detail={"error": "user list cant be empty!"})
        return user_list

    @validator("send_method_list")
    def check_send_method_list(cls, send_method_list):
        send_methods = ["sms", "email"]
        if not set(send_method_list).issubset(send_methods):
            raise HTTPException(status_code=422, detail={"error": "send method is not acceptable!"})
        return send_method_list

    @validator("service_data")
    def check_service_data(cls, service_data, values):
        if values["request_type"] == "payment":
            send_data = SendData(
                amount=service_data.get("amount"),
                customerId=service_data.get("customerId"),
                serviceName=service_data.get("serviceName"),
                serviceId=str(service_data.get("serviceId"))
            )
        return service_data


# u = Uis(
#     requestType="payment",
#     serviceData={"amount": "10000",
#                  "bankName": "melli",
#                  "customerId": "1",
#                  "serviceName": "offline",
#                  "serviceId": 8},
#     userList=[
#         {"user_id": "user1", "phone_number": "09126598657", "full_name": "zahra jm"}
#     ],
#     sendMethodList=[
#         "sms"
#     ],
#     customerId=7
# )
#
# {
#   "requestType": "payment",
#   "serviceData": {"amount": "10000",
#                   "customerId": "1",
#                   "serviceName": "offline",
#                  "serviceId": 8},
#   "userList": [
#    {"user_id": "user1", "phone_number": "09302828801", "full_name": "zahra", "city":"tehran", "state":"tehran"}
#   ],
#   "sendMethodList": [
#        "sms"
#   ],
#   "customerId": 5
# }

