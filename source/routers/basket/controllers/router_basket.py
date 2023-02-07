import json
from fastapi import APIRouter, Response, Depends, HTTPException, status, Query, Header
from source.routers.customer.module.auth import AuthHandler
from typing import Optional, List
from source.routers.basket.validators.basket import SortType, SortName, AddToCart, DeleteBasket
from source.message_broker.rabbit_server import RabbitRPC
from datetime import datetime
from source.routers.basket.modules.date_convertor import jalali_datetime
from source.routers.product.modules.allowed_storages import get_allowed_storages

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
        searchPhrase: Optional[str] = Query(None, min_length=3, max_length=50, regex="^[\u0600-\u06FF\s0-9۰-۹]{2,32}$"),
        access: Optional[str] = Header(None),
        refresh: Optional[str] = Header(None)
):
    allowed_storages = ["1"]
    if access or refresh:
        user_data, tokens = auth_handler.check_current_user_tokens(access, refresh)
        allowed_storages = get_allowed_storages(user_data.get("user_id"))
    null_filters = {
        "page": page,
        "perPage": perPage,
        "sortType": sortType,
        "sortName": sortName,
        "search": searchPhrase,
        "filters": {
            "basketStatus": ["active"],
            "storageId": allowed_storages,
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
    # checking whole sales and per day with order service
    new_baskets = []
    if type(product_data.get("data")) == list and len(product_data.get("data")):
        for basket in product_data.get("data"):
            with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
                rpc.response_len_setter(response_len=1)
                order_result = rpc.publish(
                    message={
                        "order": {
                            "action": "limit_basket_count",
                            "body": {
                                "user_id": None,
                                "basket_id": basket.get("basketId"),
                                "today": True
                            }
                        }
                    },
                    headers={'order': True}
                )
            today_order_result = order_result.get("order", {})
            if not today_order_result.get("success") or today_order_result.get("total_sell") >= basket.get(
                    "basketSalesPerDay"):
                continue
            with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
                rpc.response_len_setter(response_len=1)
                order_result = rpc.publish(
                    message={
                        "order": {
                            "action": "limit_basket_count",
                            "body": {
                                "user_id": None,
                                "basket_id": basket.get("basketId"),
                                "today": False
                            }
                        }
                    },
                    headers={'order': True}
                )
            whole_order_result = order_result.get("order", {})
            if not whole_order_result.get("success") or whole_order_result.get("total_sell") >= basket.get(
                    "basketSalesNumber"):
                continue
            new_baskets.append(basket)
    if not len(new_baskets):
        response.status_code = 404
        raise HTTPException(
            status_code=404,
            detail={"error": "سبدی برای نمایش وجود ندارد"}
        )
    response.status_code = basket_result.get("status_code", 200)
    return {"data": new_baskets, "totalCount": len(new_baskets)}


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
    product_data = product_result.get("message", {}).get("data", [])[0]
    body = {
        "user_id": user_data.get('user_id'),
        "basket_id": product_data.get("basketId"),
        "basket_data": {
            "basket_name": basket_result.get("data").get("basketName"),
            "mandatory_products": product_data.get("mandatoryProducts"),
            "selective_products": product_data.get("selectiveProducts"),
            "optional_products": product_data.get("optionalProducts")
        },
        "action": data.action,
        "list_index": data.index
    }
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        order_result = rpc.publish(
            message={
                "order": {
                    "action": "limit_basket_count",
                    "body": {
                        "user_id": None,
                        "basket_id": product_data.get("basketId"),
                        "today": True
                    }
                }
            },
            headers={'order': True}
        )
    today_order_result = order_result.get("order", {})
    if not today_order_result.get("success") or today_order_result.get("total_sell") >= basket_result.get("data").get(
            "basketSalesPerDay"):
        raise HTTPException(
            status_code=422,
            detail={"error": "فروش این سبد به پایان رسیده است"}
        )
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        order_result = rpc.publish(
            message={
                "order": {
                    "action": "limit_basket_count",
                    "body": {
                        "user_id": None,
                        "basket_id": product_data.get("basketId"),
                        "today": False
                    }
                }
            },
            headers={'order': True}
        )
    whole_order_result = order_result.get("order", {})
    if not whole_order_result.get("success") or whole_order_result.get("total_sell") >= basket_result.get("data").get(
            "basketSalesNumber"):
        raise HTTPException(
            status_code=422,
            detail={"error": "فروش این سبد به پایان رسیده است"}
        )
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


@router_basket.delete("/cart")
def delete_basket_from_cart(response: Response,
                            data: DeleteBasket,
                            auth_header=Depends(auth_handler.check_current_user_tokens)
                            ):
    user_data, header = auth_header
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        cart_result = rpc.publish(
            message={
                "cart": {
                    "action": "basket_delete_from_cart",
                    "body": {
                        "user_id": user_data.get('user_id'),
                        "basket_id": data.basket_id,
                        "list_index": data.index
                    }
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
    response.headers["accessToken"] = auth_handler.encode_refresh_token(sub_dict)
    response.headers["refresh_token"] = auth_handler.encode_access_token(sub_dict)
    response.status_code = cart_result.get("status_code", 200)
    if not cart_result.get("success"):
        raise HTTPException(status_code=cart_result.get("status_code", 500),
                            detail={"error": cart_result.get("error", "Something went wrong")})
    response.status_code = cart_result.get("status_code", 200)
    return {"message": cart_result.get("message")}
