from fastapi import HTTPException, Response, Path, APIRouter

from source.helpers.case_converter import convert_case
from source.message_broker.rabbit_server import RabbitRPC
from source.routers.customer.module.auth import AuthHandler

router = APIRouter()

auth_handler = AuthHandler()


@router.get("/{systemCode}", tags=["Kowsar"])
def get_kowsar(
        response: Response,
        system_code: str = Path(..., min_length=2, max_length=12, alias='systemCode')
):
    """
    Get kowsar item by system code
    """
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        product_result = rpc.publish(
            message={
                "product": {
                    "action": "get_kowsar",
                    "body": {
                        "system_code": system_code
                    }
                }
            },
            headers={'product': True}
        )
        product_result = product_result.get("product", {})
        if product_result.get("success"):
            response.status_code = product_result.get("status_code", 200)
            return convert_case(product_result.get("message"), 'camel')
        raise HTTPException(status_code=product_result.get("status_code", 500),
                            detail={"error": product_result.get("error", "Something went wrong")})


@router.get("/{systemCode}/items/", tags=["Kowsar"])
def get_kowsar_items(
        response: Response,
        system_code: str = Path(..., min_length=2, max_length=9, alias='systemCode')
):
    """
    Get children of kowsar item
    """
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        product_result = rpc.publish(
            message={
                "product": {
                    "action": "get_kowsar_items",
                    "body": {
                        "system_code": system_code
                    }
                }
            },
            headers={'product': True}
        )
        product_result = product_result.get("product", {})
        if product_result.get("success"):
            response.status_code = product_result.get("status_code", 200)
            return convert_case(product_result.get("message"), 'camel')
        raise HTTPException(status_code=product_result.get("status_code", 500),
                            detail={"error": product_result.get("error", "Something went wrong")})


@router.get("/update_collection", tags=["Kowsar"])
def update_kowsar_collection(
        response: Response
):
    """
    Update kowsar collection based on given file
    """
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        product_result = rpc.publish(
            message={
                "product": {
                    "action": "update_kowsar_collection",
                    "body": {}
                }
            },
            headers={'product': True}
        )
        product_result = product_result.get("product", {})
        if product_result.get("success"):
            response.status_code = product_result.get("status_code", 200)
            return convert_case(product_result.get("message"), 'camel')
        raise HTTPException(status_code=product_result.get("status_code", 500),
                            detail={"error": product_result.get("error", "Something went wrong")})
