import json

from fastapi import Response, Depends, HTTPException,Path,Body, Query
from fastapi import status, APIRouter
from source.helpers.case_converter import convert_case
from fastapi.openapi.models import RequestBody

from source.message_broker.rabbit_server import RabbitRPC

from source.routers.coupon.validators.coupon import Coupon


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
    coupon_result = coupon_result.get("coupon",{})
    if coupon_result.get("success"):
        response.status_code = coupon_result.get("status_code", 200)
        return convert_case(coupon_result.get("message"), 'camel')
    raise HTTPException(status_code=coupon_result.get("status_code", 500),
                        detail={"error": coupon_result.get("error", "Something went wrong")})


@router.post("/create",tags=["coupon_create"] )
def create_coupon( response: Response,
                  data: Coupon = Body(..., example = {

                        "title": "yalda",
                        "code_length": 4,
                        "created_time": "1400-11-27",
                        "started_at": "1400-11-27",
                        "expire_time": "1400-12-15",
                        "has_expire": False,
                        "count": 1000,
                        "assign_customers": [
                            1234, 1258, 1584
                        ],
                        "user_limit": 10,
                        "assign_customer_groups": [
                            1234, 1258, 1584
                        ],
                        "min_order_price": 500,
                        "min_order": 200,
                        "item_count": 20,
                        "value": 20,
                        "max_value": 200,
                        "value_type": "percent",
                        "is_enabled": True,
                        "coupon_codes": [
                            {"coupon_ID": "GE-123", "used": 0}, {"coupon_ID": "RF-456", "used": 1}
                        ],
                        "prefix": "GE",
                        "suffix": "RE",
                        "assigned_product": [
                            "mobile", "notebook", "headset"
                        ],
                        "assigned_events": [
                            "yalda", "nouruz"
                        ],
                        "coupon_types": 5,
                        "used_count": {'customer_id': 1234, "use_count": 0},

                        "fixed_name": True
                    })
                    ) -> dict:
    """
    Generate a coupon and add to coupon collection in database with this information:
    """
    rpc.response_len_setter(response_len=1)
    coupon_result = rpc.publish(
        message={
            "coupon": {
                "action": "create_coupon",
                "body": {"coupon":dict(data)}
            }
        },
        headers={'coupon': True}
    )
    coupon_result = coupon_result.get("coupon", {})
    if coupon_result.get("success"):
        response.status_code = coupon_result.get("status_code", 200)
        return convert_case(coupon_result.get("message"), 'camel')
    raise HTTPException(status_code=coupon_result.get("status_code", 500),
                        detail={"error": coupon_result.get("error", "Coupon service Internal error")})


@router.get('/{coupon_types}')
def get_coupons_by_filter(response: Response,coupon_types: int =Path(...,)):
    """
    Get coupons with filter
    """

    rpc.response_len_setter(response_len=1)
    coupon_result = rpc.publish(
        message={
            "coupon":{
                "action":"get_coupons_by_filter",
                "body":{
                    "coupon_types":coupon_types
                }
            }
        },
        headers={"coupon":True}
    )
    coupon_result = coupon_result.get("coupon", {})
    if coupon_result.get("success"):
        response.status_code = coupon_result.get("status_code", 200)
        return convert_case(coupon_result.get("message"), 'camel')
    raise HTTPException(status_code=coupon_result.get("status_code", 500),
                        detail={"error": coupon_result.get("error", "Coupon service Internal error")})


@router.get('/list/{codes}', status_code=200)
def get_code_list():
    """
     Get list of coupon codes
     """
    coupon = Coupon.construct()
    return coupon.get_list_coupon_code()


@router.get('/coupon_id/{coupon_id}')
def get_by_coupon_id(response: Response,coupon_id:int):
    """
     Get coupon_id
     """
    rpc.response_len_setter(response_len=1)
    coupon_result = rpc.publish(
        message={
            "coupon": {
                "action": "get_by_coupon_id",
                "body": {"coupon": coupon_id
                }
            }

        },
        headers={'coupon': True}
    )
    coupon_result = coupon_result.get("product", {})
    if coupon_result.get("success"):
        response.status_code = coupon_result.get("status_code", 200)
        return convert_case(coupon_result.get("message"), 'camel')
    raise HTTPException(status_code=coupon_result.get("status_code", 500),
                        detail={"error": coupon_result.get("error", "Something went wrong")})




@router.put('/{coupon_id}')
def update_coupon(coupon_id: str, response: Response):
    """
    Update the coupon_id in database.
    """
    rpc.response_len_setter(response_len=1)
    product_result = rpc.publish(
        message={
            "coupon": {
                "action": "update_coupon",
                "body": {
                    "coupon_id": coupon_id
                }
            }
        },
        headers={'coupon': True}
    )
    coupon_result = product_result.get("coupon", {})
    if coupon_result.get("success"):
        response.status_code = coupon_result.get("status_code", 200)
        return convert_case(coupon_result.get("message"), 'camel')
    raise HTTPException(status_code=coupon_result.get("status_code", 500),
                        detail={"error": coupon_result.get("error", "Something went wrong")})

@router.put('/disable/{coupon_id}')
def disable_coupon(coupon_id: str,response: Response):
    """
    disable coupon_id
    """
    rpc.response_len_setter(response_len=1)
    product_result = rpc.publish(
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
    coupon_result = product_result.get("coupon", {})
    if coupon_result.get("success"):
        response.status_code = coupon_result.get("status_code", 200)
        return convert_case(coupon_result.get("message"), 'camel')
    raise HTTPException(status_code=coupon_result.get("status_code", 500),
                        detail={"error": coupon_result.get("error", "Something went wrong")})



@router.post('/request', status_code=200)
def check_request(request: RequestBody):
    message, success = request.check_request()
    if success:
        return message
    raise HTTPException(status_code=417, detail=message)
