import json

from fastapi import APIRouter
from source.message_broker.rabbit_server import RabbitRPC
from source.routers.customer.module.auth import AuthHandler

router_coupon = APIRouter(
    prefix="/coupon",
    tags=["coupon"]
)
auth_handler = AuthHandler()


@router_coupon.post("/add")
def mobile_number_validation_generator():
    """
    generate and send mobile number validations to front side
    :return: front-end required values for generate form
    """
    return True
