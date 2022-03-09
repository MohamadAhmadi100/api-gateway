from fastapi import Response, Depends, HTTPException, Path, Body, Query
from fastapi import status, APIRouter
from source.helpers.case_converter import convert_case

from source.message_broker.rabbit_server import RabbitRPC

from source.routers.coupon.validators.coupon import Coupon, RequestBody

# from customer.mudoles import log

router = APIRouter()

rpc = RabbitRPC(exchange_name='headers_exchange', timeout=5)
rpc.connect()
rpc.consume()


@router.get('/{page}')
def get_all_coupons(
        response: Response,
        page: int = Path(1, ge=1, le=1000),
        per_page: int = Query(10, ge=1, le=1000)
) -> list:
    """
      Get all available coupons in database.
      """
    rpc.response_len_setter(response_len=1)
    coupon_result = rpc.publish(
        message={
            "coupon": {
                "action": "get_all_coupons",
                "body": {
                    "page": page,
                    "per_page": per_page
                }
            }
        },
        headers={'coupon': True}
    )
    coupon_result = coupon_result.get("coupon", {})
    if coupon_result.get("success"):
        response.status_code = coupon_result.get("status_code", 200)
        return convert_case(coupon_result.get("message"), 'camel')
    raise HTTPException(status_code=coupon_result.get("status_code", 500),
                        detail={"error": coupon_result.get("error", "Something went wrong")})


@router.post("/create", tags=["coupon_create"])
def create_coupon(response: Response,
                  coupon: Coupon
                  ):
    """
    Generate a coupon and add to coupon collection in database with this information:
    """
    rpc.response_len_setter(response_len=1)
    result = rpc.publish(
        message={
            "coupon": {
                "action": "create_coupon",
                "body": {
                    "item": coupon.dict()
                }

            }
        },
        headers={'coupon': True}
    )
    coupon_result = result.get("coupon", {})
    if coupon_result.get("success"):
        response.status_code = coupon_result.get("status_code", 200)
        return convert_case(coupon_result.get("message"), 'camel')
    raise HTTPException(status_code=coupon_result.get("status_code", 500),
                        detail={"error": coupon_result.get("error", "Coupon service Internal error")})


@router.get('/lists/{coupon_types}')
def get_coupons_by_filter(response: Response, coupon_types: int = Path(..., )):
    """
    Get coupons with filter
    """

    rpc.response_len_setter(response_len=1)
    result = rpc.publish(
        message={
            "coupon": {
                "action": "get_coupons_by_filter",
                "body": {
                    "coupon_types": coupon_types
                }
            }
        },
        headers={"coupon": True}
    )
    coupon_result = result.get("coupon", {})
    if coupon_result.get("success"):
        response.status_code = coupon_result.get("status_code", 200)
        return convert_case(coupon_result.get("message"), 'camel')
    raise HTTPException(status_code=coupon_result.get("status_code", 500),
                        detail={"error": coupon_result.get("error", "Coupon service Internal error")})


@router.get('/lists/', status_code=200)
def get_code_list(response: Response):
    """
     Get list of coupon codes
     """
    rpc.response_len_setter(response_len=1)
    result = rpc.publish(
        message={
            "coupon": {
                "action": "get_code_list",
                "body": {

                }
            }
        },
        headers={"coupon": True}
    )
    coupon_result = result.get("coupon", {})
    if coupon_result.get("success"):
        response.status_code = coupon_result.get("status_code", 200)
        return convert_case(coupon_result.get("message"), 'camel')
    raise HTTPException(status_code=coupon_result.get("status_code", 500),
                        detail={"error": coupon_result.get("error", "Coupon service Internal error")})


@router.get('/coupons/{coupon_id}')
def get_by_coupon_id(response: Response, coupon_id: str):
    """
     Get coupon_id
     """
    rpc.response_len_setter(response_len=1)
    result = rpc.publish(
        message={
            "coupon": {
                "action": "get_by_coupon_id",
                "body": {
                    "coupon_id": coupon_id
                }
            }

        },
        headers={'coupon': True}
    )
    coupon_result = result.get("coupon", {})
    if coupon_result.get("success"):
        response.status_code = coupon_result.get("status_code", 200)
        return convert_case(coupon_result.get("message"), 'camel')
    raise HTTPException(status_code=coupon_result.get("status_code", 500),
                        detail={"error": coupon_result.get("error", "Something went wrong")})


@router.put('/{coupon_id}')
def update_coupon(coupon_id: str, coupon: Coupon, response: Response):
    """
    Update the coupon_id in database.
    """
    rpc.response_len_setter(response_len=1)
    result = rpc.publish(
        message={
            "coupon": {
                "action": "update_coupon",
                "body": {
                    "coupon_id": coupon_id,
                    "coupon": coupon.dict()
                }
            }
        },
        headers={'coupon': True}
    )
    coupon_result = result.get("coupon", {})
    if coupon_result.get("success"):
        response.status_code = coupon_result.get("status_code", 200)
        return convert_case(coupon_result.get("message"), 'camel')
    raise HTTPException(status_code=coupon_result.get("status_code", 500),
                        detail={"error": coupon_result.get("error", "Something went wrong")})


@router.put('/disable/{coupon_id}')
def disable_coupon(coupon_id: str, response: Response):
    """
    disable coupon_id
    """
    rpc.response_len_setter(response_len=1)
    result = rpc.publish(
        message={
            "coupon": {
                "action": "disable_coupon",
                "body": {
                    "coupon_id": coupon_id
                }
            }
        },
        headers={'coupon': True}
    )
    coupon_result = result.get("coupon", {})
    if coupon_result.get("success"):
        response.status_code = coupon_result.get("status_code", 200)
        return convert_case(coupon_result.get("message"), 'camel')
    raise HTTPException(status_code=coupon_result.get("status_code", 500),
                        detail={"error": coupon_result.get("error", "Something went wrong")})


@router.post('/request', status_code=200)
def check_request(request: RequestBody, response: Response):
    rpc.response_len_setter(response_len=1)
    result = rpc.publish(
        message={
            "coupon": {
                "action": "check_request",
                "body": {
                    "request": request.dict()
                }
            }
        },
        headers={"coupon": True}
    )
    coupon_result = result.get('coupon', {})
    if coupon_result.get("success"):
        response.status_code = coupon_result.get("status_code", 200)
        return convert_case(coupon_result.get("message"), 'camel')
    raise HTTPException(status_code=coupon_result.get("status_code", 500),
                        detail={"error": coupon_result.get("error", "Something went wrong")})


@router.get('/request/{customer_ID}', status_code=200)
def get_customer_info(customer_ID: int, response: Response):
    rpc.response_len_setter(response_len=1)
    result = rpc.publish(
        message={
            "coupon": {
                "action": "get_customer_info",
                "body": {
                    'customer_ID': customer_ID
                }
            }
        },
        headers={"coupon": True}
    )
    coupon_result = result.get('coupon', {})
    if coupon_result.get("success"):
        response.status_code = coupon_result.get("status_code", 200)
        return convert_case(coupon_result.get("message"), 'camel')
    raise HTTPException(status_code=coupon_result.get("status_code", 500),
                        detail={"error": coupon_result.get("error", "Something went wrong")})
