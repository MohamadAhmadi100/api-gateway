import json

from fastapi import Response, Depends, HTTPException
from fastapi import status, APIRouter

from source.message_broker.rabbit_server import RabbitRPC

from source.routers.coupon.validators.coupon import Coupon

# from customer.mudoles import log

router = APIRouter()

rpc = RabbitRPC(exchange_name='headers_exchange', timeout=5)
rpc.connect()
rpc.consume()


@router.get('/{page}', status_code=200)
def get_all_coupons(
        page: int = Path(1, ge=1, le=1000),
        per_page: int = Query(10, ge=1, le=1000)
) -> list:
    coupon = Coupon.construct()
    data = coupon.get(page=page, per_page=per_page)
    if data:
        return data
    raise HTTPException(status_code=404, detail={'message': 'collection is empty'})


@router.post('/', status_code=201)
def create_coupon(coupon: Coupon = Body(
    ...,
    example={
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
    })):
    """
    """
    message, success, code = coupon.create()
    if success:
        return message, code
    raise HTTPException(status_code=404, detail=message)


@router.get('/{coupon_types}', status_code=200)
def get_coupons_by_filter(coupon_types: int):
    coupons = Coupon.construct()
    data = coupons.get(coupon_types)
    if data:
        return data
    raise HTTPException(status_code=404, detail={'message': 'Not found'})


@router.get('/list/code', status_code=200)
def get_code_list():
    coupon = Coupon.construct()
    return coupon.get_list_coupon_code()


@router.get('/coupon_id/{coupon_id}')
def get_by_coupon_id(coupon_id):
    coupon = Coupon.construct()
    return coupon.get_by_coupon_id(coupon_id)


@router.put('/{coupon_id}', status_code=201)
def update_coupon(coupon_id: str, coupons: Coupon):
    coupon = Coupon.construct()
    stored_data = coupon.get_by_coupon_id(coupon_id)
    updated_data = coupons.dict(exclude_unset=True)
    updated_item = stored_data.copy(update=updated_data)
    message, success = coupons.update(updated_item.dict())
    if success:
        return message
    raise HTTPException(status_code=417, detail=message)


@router.put('/disable/{coupon_id}', status_code=201)
def disable_coupon(coupon_id: str):
    coupon = Coupon.construct()
    return coupon.disable(coupon_id)


@router.post('/request', status_code=200)
def check_request(request: RequestBody):
    message, success = request.check_request()
    if success:
        return message
    raise HTTPException(status_code=417, detail=message)
