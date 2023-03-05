from fastapi import Depends, APIRouter, Response
from source.message_broker.rabbit_server import RabbitRPC
from source.routers.customer.module.auth import AuthHandler
from source.routers.dealership.validators.return_products_validator import Return

router = APIRouter()
auth_handler = AuthHandler()


@router.post("/create_return_form", tags=["return products"])
def create_return_form(data: Return,
                 response: Response,
                 auth_header=Depends(auth_handler.check_current_user_tokens)):
    user, token = auth_header
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        rpc.response_len_setter(response_len=1)
        customer_response = rpc.publish(
            message={
                "customer": {
                    "action": "get_profile",
                    "body": {
                        "customer_phone_number": user
                    }
                }
            },
            headers={'customer': True}
        ).get("customer", {})
        if customer_response.get("success"):
            for item in customer_response.get("message"):
                if item.get("name") == "customerFirstName":
                    customer_first_name = item.get("value")
                if item.get("name") == "customerLastName":
                    customer_last_name = item.get("value")
        dealership_response = rpc.publish(
            message={
                "dealership": {
                    "action": "return_product",
                    "body": {
                        "dealership_id": str(user.get("user_id")),
                        "dealership_phone_number": str(user.get("phone_number")),
                        "customer_name": customer_first_name + " " + customer_last_name,
                        "products": data.dict().get("products")
                    }
                }
            },
            headers={'dealership': True}
        ).get("dealership", {})
        if dealership_response.get("success"):
            response.status_code = dealership_response.get("status_code", 201)
            return dealership_response
