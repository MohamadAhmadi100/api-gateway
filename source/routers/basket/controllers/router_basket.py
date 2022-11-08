import json
from fastapi import APIRouter, Response, Depends, HTTPException, status, Query
from source.routers.customer.module.auth import AuthHandler
from typing import Optional, List
from source.routers.basket.validators.basket import SortType, SortName, AddToCart
from source.message_broker.rabbit_server import RabbitRPC
from datetime import datetime
from source.routers.basket.modules.date_convertor import jalali_datetime

router_basket = APIRouter(
    prefix="/basket",
    tags=["basket"]
)
auth_handler = AuthHandler()


@router_basket.get("/baskets")
def get_baskets(
        response: Response,
        page: Optional[int] = None,
        perPage: Optional[int] = None,
        sortType: Optional[SortType] = None,
        sortName: Optional[SortName] = None,
        storageId: Optional[List[str]] = Query(None),
        searchPhrase: Optional[str] = Query(None, min_length=3, max_length=50, regex="^[\u0600-\u06FF\s0-9۰-۹]{2,32}$"),
        # auth_header=Depends(auth_handler.check_current_user_tokens)
):
    null_filters = {
        "page": page,
        "perPage": perPage,
        "sortType": sortType,
        "sortName": sortName,
        "search": searchPhrase,
        "filters": {
            "basketStatus": ["active"],
            "storageId": storageId,
            "basketJalaliStartDate": {
                "start": jalali_datetime(datetime.now()),
            },
            "basketJalaliEndDate": {
                "end": jalali_datetime(datetime.now()),
            }
        }
    }
    filters = {key: value for key, value in null_filters.items() if value}
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        basket_result = rpc.publish(
            message={
                "basket": {
                    "action": "get_all_available_baskets",
                    "body": {
                        "data": json.dumps(filters)
                    }
                }
            },
            headers={'basket': True}
        )
    basket_result = basket_result.get("basket", {})
    if not basket_result.get("success"):
        raise HTTPException(
            status_code=basket_result.get("status_code", 500),
            detail={"error": basket_result.get("error", "Something went wrong")}
        )
    # checking basket products with product service
    baskets = basket_result.get("message").get("data")
    if type(baskets) != list or not len(baskets):
        raise HTTPException(
            status_code=404,
            detail={"error": "سبدی برای نمایش موجود نیست"}
        )
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        result = rpc.publish(
            message={
                "product": {
                    "action": "get_basket_products",
                    "body": {
                        "data": baskets,
                        "customer_type": "B2B"
                    }
                }
            },
            headers={'product': True}
        )
    product_result = result.get("product", {})
    if not product_result.get("success"):
        raise HTTPException(
            status_code=product_result.get("status_code", 500),
            detail={"error": product_result.get("error", "Something went wrong")}
        )
    product_data = product_result.get("message", {})
    response.status_code = basket_result.get("status_code", 200)
    # checking whole sales and per day with order service
    return product_data


@router_basket.put("/cart")
def add_or_edit_cart(response: Response,
                     data: AddToCart,
                     auth_header=Depends(auth_handler.check_current_user_tokens)
                     ):
    user_data, header = auth_header
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        basket_result = rpc.publish(
            message={
                "basket": {
                    "action": "check_basket_is_valid",
                    "body": {
                        "data": data.json(),
                    }
                }
            },
            headers={'basket': True}
        )
    basket_result = basket_result.get("basket", {})
    if not basket_result.get("success"):
        raise HTTPException(
            status_code=basket_result.get("status_code", 500),
            detail={"error": basket_result.get("error", "Something went wrong")}
        )
    # checking basket products with product service
    baskets = [basket_result.get("data")]
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        result = rpc.publish(
            message={
                "product": {
                    "action": "get_basket_products",
                    "body": {
                        "data": baskets,
                        "customer_type": "B2B"
                    }
                }
            },
            headers={'product': True}
        )
    product_result = result.get("product", {})
    if not product_result.get("success"):
        raise HTTPException(
            status_code=product_result.get("status_code", 500),
            detail={"error": product_result.get("error", "Something went wrong")}
        )
    product_data = product_result.get("message", {})[0]
    body = {
        "user_id": user_data.get('user_id'),
        "basket_id": product_data.get("basketId"),
        "basket_data": {
            "mandatory_products": product_data.get("mandatoryProducts"),
            "selective_products": product_data.get("selectiveProducts"),
            "optional_products": product_data.get("optionalProducts")
        },
        "action": data.action,
        "list_index": data.index
    }
    # todo: checking whole sales and per day with order service
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        cart_result = rpc.publish(
            message={
                "cart": {
                    "action": "basket_add_to_cart",
                    "body": body
                }
            },
            headers={'cart': True}
        )
    cart_result = cart_result.get("cart", {})
    sub_dict = {
        "user_id": user_data.get('user_id'),
        "customer_type": user_data.get('customer_type'),
        "phone_number": user_data.get('phone_number'),
    }
    response.status_code = status.HTTP_200_OK
    response.headers["accessToken"] = auth_handler.encode_refresh_token(sub_dict)
    response.headers["refresh_token"] = auth_handler.encode_access_token(sub_dict)
    response.status_code = basket_result.get("status_code", 200)
    if not cart_result.get("success"):
        raise HTTPException(status_code=cart_result.get("status_code", 500),
                            detail={"error": cart_result.get("error", "Something went wrong")})
    response.status_code = cart_result.get("status_code", 200)
    return {"message": cart_result.get("message")}
