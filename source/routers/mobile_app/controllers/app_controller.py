from typing import Optional

from fastapi import APIRouter, Response, HTTPException, Path, Query

from source.helpers.case_converter import convert_case
from source.message_broker.rabbit_server import RabbitRPC
from source.routers.mobile_app.validators.model import ForceUpdate

router = APIRouter()


@router.post("/forceUpdate", tags=["ForceUpdate"])
def insert_force_update(
        response: Response,
        force_update: ForceUpdate
):
    """
    Insert force update
    """
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        product_result = rpc.publish(
            message={
                "mobile_app": {
                    "action": "insert_force_update",
                    "body": force_update.__dict__
                }
            },
            headers={'mobile_app': True}
        )
        product_result = product_result.get("mobile_app", {})
        if product_result.get("success"):
            response.status_code = product_result.get("status_code", 200)
            return convert_case({"message": product_result.get("message")}, 'camel')
        raise HTTPException(status_code=product_result.get("status_code", 500),
                            detail={"error": product_result.get("error", "Something went wrong")})


@router.get("/forceUpdate", tags=["ForceUpdate"])
def get_force_update(
        response: Response,
        os_type: Optional[str] = Query(None)
):
    """
    Get force update
    """
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        product_result = rpc.publish(
            message={
                "mobile_app": {
                    "action": "get_force_update",
                    "body": {"os_type": os_type}
                }
            },
            headers={'mobile_app': True}
        )
        product_result = product_result.get("mobile_app", {})
        if product_result.get("success"):
            response.status_code = product_result.get("status_code", 200)
            return convert_case({"message": product_result.get("message")}, 'camel')
        raise HTTPException(status_code=product_result.get("status_code", 500),
                            detail={"error": product_result.get("error", "Something went wrong")})
