import datetime
from typing import Optional, List

from fastapi import HTTPException, APIRouter, Response, Path, Query, Header

from source.helpers.case_converter import convert_case
from source.message_broker.rabbit_server import RabbitRPC
from source.routers.customer.module.auth import AuthHandler
from source.routers.product.modules.allowed_storages import get_allowed_storages

router = APIRouter()

auth_handler = AuthHandler()


@router.get("/product/stock/{systemCode}/", tags=["Product"])
def get_product_stock(response: Response,
                      system_code: str = Path(..., min_length=25, max_length=25, alias="systemCode")) -> dict:
    """
    get product stock
    """
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        quantity_result = rpc.publish(
            message={
                "product": {
                    "action": "get_stock",
                    "body": {
                        "system_code": system_code
                    }
                }
            },
            headers={'product': True}
        )
        quantity_result = quantity_result.get("product", {})
        if quantity_result.get("success"):
            response.status_code = quantity_result.get("status_code", 200)
            return convert_case(quantity_result.get("message"), action='camel')
        raise HTTPException(status_code=quantity_result.get("status_code", 500),
                            detail=convert_case({"error": quantity_result.get("error", "Something went wrong")},
                                                action="camel"))


@router.get("/get_product_list_by_system_code/{systemCode}/", tags=["Product"])
def get_product_list_by_system_code(
        response: Response,
        system_code: str = Path(..., alias='systemCode'),
        page: int = Query(1, alias='page'),
        per_page: int = Query(10, alias='perPage'),
        storages: List[str] = Query([], alias='storages'),
        customer_type: str = Query("B2B", alias="customerType"),
        access: Optional[str] = Header(None),
        refresh: Optional[str] = Header(None)
):
    """
    Get product list by brand
    """
    allowed_storages = []
    if access or refresh:
        user_data, tokens = auth_handler.check_current_user_tokens(access, refresh)
        customer_type = user_data.get("customer_type", ["B2B"])[0]
        customer_type = customer_type if not customer_type == "B2B2C" else "B2B"
        allowed_storages = get_allowed_storages(user_data.get("user_id"))
        user_allowed_storages = [storage for storage in storages if
                                 storage in allowed_storages] if storages else allowed_storages
        if not user_allowed_storages:
            raise HTTPException(status_code=404, detail={"error": "No products found"})

    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        product_result = rpc.publish(
            message={
                "product": {
                    "action": "get_product_list_by_system_code",
                    "body": {
                        "system_code": system_code,
                        "page": page,
                        "per_page": per_page,
                        "storages": storages,
                        "user_allowed_storages": allowed_storages,
                        "customer_type": customer_type
                    }
                }
            },
            headers={'product': True}
        )
        product_result = product_result.get("product", {})
        if product_result.get("success"):
            product_result = product_result.get("message", {})
            response.status_code = product_result.get("status_code", 200)
            return convert_case(product_result, 'camel')
        raise HTTPException(status_code=product_result.get("status_code", 500),
                            detail={"error": product_result.get("error", "Something went wrong")})


# product page get api
@router.get("/product/get_product_page/{systemCode}/{lang}/", tags=["Product"])
def get_product_page(
        response: Response,
        system_code: str = Path(..., alias='systemCode', max_length=16, min_length=16),
        customer_type: str = Query("B2B", alias="customerType"),
        lang: Optional[str] = Path("fa_ir", min_length=2, max_length=8),
        access: Optional[str] = Header(None),
        refresh: Optional[str] = Header(None)
):
    """
    Get product page
    """
    allowed_storages = []
    credit = False
    if access or refresh:
        user_data, tokens = auth_handler.check_current_user_tokens(access, refresh)
        customer_type = user_data.get("customer_type", ["B2B"])[0]
        customer_type = customer_type if not customer_type == "B2B2C" else "B2B"
        allowed_storages = get_allowed_storages(user_data.get("user_id"))
        credit_expire_date = user_data.get("sub", {}).get("credit_expire_date")
        credit = user_data.get("sub", {}).get("credit", False)
        if credit and datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") > credit_expire_date:
            credit = True

    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        product_result = rpc.publish(
            message={
                "product": {
                    "action": "get_product_page",
                    "body": {
                        "system_code": system_code,
                        "user_allowed_storages": allowed_storages,
                        "customer_type": customer_type,
                        "lang": lang,
                        "credit": credit
                    }
                }
            },
            headers={'product': True}
        )
        product_result = product_result.get("product", {})
        if product_result.get("success"):
            product_result = product_result.get("message", {})
            response.status_code = product_result.get("status_code", 200)
            return convert_case(product_result, 'camel')
        raise HTTPException(status_code=product_result.get("status_code", 500),
                            detail={"error": product_result.get("error", "Something went wrong")})


@router.get("/product/get_product_by_name/{name}/", tags=["Product"])
def get_product_by_name(name: str,
                        response: Response,
                        storages: List[str] = Query([], alias='storages'),
                        customer_type: str = Query("B2B", alias="customerType"),
                        access: Optional[str] = Header(None),
                        refresh: Optional[str] = Header(None)
                        ):
    allowed_storages = []
    if access or refresh:
        user_data, tokens = auth_handler.check_current_user_tokens(access, refresh)
        customer_type = user_data.get("customer_type", ["B2B"])[0]
        customer_type = customer_type if not customer_type == "B2B2C" else "B2B"
        allowed_storages = get_allowed_storages(user_data.get("user_id"))
        user_allowed_storages = [storage for storage in storages if
                                 storage in allowed_storages] if storages else allowed_storages
        if not user_allowed_storages:
            raise HTTPException(status_code=404, detail={"error": "No products found"})

    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        product_result = rpc.publish(
            message={
                "product": {
                    "action": "get_product_by_name",
                    "body": {
                        "name": name,
                        "storages": storages,
                        "user_allowed_storages": allowed_storages,
                        "customer_type": customer_type,
                    }
                }
            },
            headers={'product': True}
        )
        product_result = product_result.get("product", {})
        if product_result.get("success"):
            message_product = product_result.get("message", {})
            response.status_code = product_result.get("status_code", 200)
            return convert_case(message_product, 'camel')
        raise HTTPException(status_code=product_result.get("status_code", 500),
                            detail={"error": product_result.get("error", "Something went wrong")})


@router.get("/get_category_list", tags=["Product"])
def get_category_list(
        response: Response,
        customer_type: str = Query("B2B", alias="customerType"),
        access: Optional[str] = Header(None),
        refresh: Optional[str] = Header(None)
):
    """
    Get category list
    """
    allowed_storages = []
    if access or refresh:
        user_data, tokens = auth_handler.check_current_user_tokens(access, refresh)
        customer_type = user_data.get("customer_type", ["B2B"])[0]
        customer_type = customer_type if not customer_type == "B2B2C" else "B2B"
        allowed_storages = get_allowed_storages(user_data.get("user_id"))

    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)

        product_result = rpc.publish(
            message={
                "product": {
                    "action": "get_category_list",
                    "body": {
                        "user_allowed_storages": allowed_storages,
                        "customer_type": customer_type,
                    }
                }
            },
            headers={'product': True}
        )
        product_result = product_result.get("product", {})
        if product_result.get("success"):
            message_product = product_result.get("message", {})
            response.status_code = product_result.get("status_code", 200)
            return convert_case(message_product, 'camel')
        raise HTTPException(status_code=product_result.get("status_code", 500),
                            detail={"error": product_result.get("error", "Something went wrong")})


@router.get("/price_list/", tags=['Product'])
def price_list(
        response: Response,
        customer_type: str = Query("B2B"),
        storage_id: str = Query(None),
        sub_category: str = Query(None),
        brand: str = Query(None),
        model: str = Query(None),
        access: Optional[str] = Header(None),
        refresh: Optional[str] = Header(None),
):
    allowed_storages = []
    if access or refresh:
        user_data, tokens = auth_handler.check_current_user_tokens(access, refresh)
        customer_type = user_data.get("customer_type", ["B2B"])[0]
        customer_type = customer_type if not customer_type == "B2B2C" else "B2B"
        allowed_storages = get_allowed_storages(user_data.get("user_id"))

    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        product_result = rpc.publish(
            message={
                "product": {
                    "action": "price_list",
                    "body": {
                        "customer_type": customer_type,
                        "storage_id": storage_id,
                        "sub_category": sub_category,
                        "brand": brand,
                        "model": model,
                        "allowed_storages": allowed_storages
                    }
                }
            },
            headers={'product': True}
        )
        product_result = product_result.get("product", {})
        if product_result.get("success"):
            message_product = product_result.get("message", {})
            response.status_code = product_result.get("status_code", 200)
            return convert_case(message_product, 'camel')
        raise HTTPException(status_code=product_result.get("status_code", 500),
                            detail={"error": product_result.get("error", "Something went wrong")})


@router.get("/price_list_tehran/", tags=['Product'])
def price_list_tehran(
        response: Response,
        customer_type: str = Query("B2B"),
        sub_category: str = Query(None),
        brand: str = Query(None),
        model: str = Query(None),
):
    allowed_storages = ['1', '7']

    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        product_result = rpc.publish(
            message={
                "product": {
                    "action": "price_list_tehran",
                    "body": {
                        "customer_type": customer_type,
                        "sub_category": sub_category,
                        "brand": brand,
                        "model": model,
                        "allowed_storages": allowed_storages
                    }
                }
            },
            headers={'product': True}
        )
        product_result = product_result.get("product", {})
        if product_result.get("success"):
            message_product = product_result.get("message", {})
            response.status_code = product_result.get("status_code", 200)
            return convert_case(message_product, 'camel')
        raise HTTPException(status_code=product_result.get("status_code", 500),
                            detail={"error": product_result.get("error", "Something went wrong")})


@router.get("/price_list_all/", tags=['Product'])
def price_list_all(
        response: Response,
        customer_type: Optional[str] = Query("B2B"),
        sub_category: str = Query(None),
        brand: str = Query(None),
        model: str = Query(None),
        access: Optional[str] = Header(None),
        refresh: Optional[str] = Header(None),
):
    allowed_storages = []
    if access or refresh:
        user_data, tokens = auth_handler.check_current_user_tokens(access, refresh)
        customer_type = user_data.get("customer_type", ["B2B"])[0]
        customer_type = customer_type if not customer_type == "B2B2C" else "B2B"
        allowed_storages = get_allowed_storages(user_data.get("user_id"))

    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        product_result = rpc.publish(
            message={
                "product": {
                    "action": "price_list_all",
                    "body": {
                        "customer_type": customer_type,
                        "sub_category": sub_category,
                        "brand": brand,
                        "model": model,
                        "allowed_storages": allowed_storages
                    }
                }
            },
            headers={'product': True}
        )
        product_result = product_result.get("product", {})
        if product_result.get("success"):
            message_product = product_result.get("message", {})
            response.status_code = product_result.get("status_code", 200)
            return convert_case(message_product, 'camel')
        raise HTTPException(status_code=product_result.get("status_code", 500),
                            detail={"error": product_result.get("error", "Something went wrong")})


@router.get("/get_csv/", tags=['Product'])
def get_csv(
        storage_id: str,
        response: Response,
):
    """
    Get csv
    """
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        product_result = rpc.publish(
            message={
                "product": {
                    "action": "get_csv",
                    "body": {
                        "storage_id": storage_id
                    }
                }
            },
            headers={'product': True}
        )
        product_result = product_result.get("product", {})
        if product_result.get("success"):
            message_product = product_result.get("message", {})
            response.status_code = product_result.get("status_code", 200)
            return Response(content=message_product.encode("utf-8-sig"), media_type="text/csv")
        raise HTTPException(status_code=product_result.get("status_code", 500),
                            detail={"error": product_result.get("error", "Something went wrong")})


@router.get("/get_data_price_list_pic/", tags=['Product'])
def get_data_price_list_pic(
        response: Response,
        system_code: str,
        customer_type: str = Query("B2B"),
        page: int = Query(None),
        per_page: int = Query(None),
        storage_id: str = Query(None)
):
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        product_result = rpc.publish(
            message={
                "product": {
                    "action": "get_data_price_list_pic",
                    "body": {
                        "system_code": system_code,
                        "customer_type": customer_type,
                        "page": page,
                        "per_page": per_page,
                        "storage_id": storage_id
                    }
                }
            },
            headers={'product': True}
        )
        product_result = product_result.get("product", {})
        if product_result.get("success"):
            message_product = product_result.get("message", {})
            response.status_code = product_result.get("status_code", 200)
            return convert_case(message_product, 'camel')
        raise HTTPException(status_code=product_result.get("status_code", 500),
                            detail={"error": product_result.get("error", "Something went wrong")})


@router.get("/get_mega_menu/", tags=['Product'])
def get_mega_menu(
        response: Response,
        customer_type: str = Query("B2B"),
        access: Optional[str] = Header(None),
        refresh: Optional[str] = Header(None),
):
    allowed_storages = []
    if access or refresh:
        user_data, tokens = auth_handler.check_current_user_tokens(access, refresh)
        customer_type = user_data.get("customer_type", ["B2B"])[0]
        customer_type = customer_type if not customer_type == "B2B2C" else "B2B"
        allowed_storages = get_allowed_storages(user_data.get("user_id"))

    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        product_result = rpc.publish(
            message={
                "product": {
                    "action": "get_mega_menu",
                    "body": {
                        "customer_type": customer_type,
                        "user_allowed_storages": allowed_storages
                    }
                }
            },
            headers={'product': True}
        )
        product_result = product_result.get("product", {})
        if product_result.get("success"):
            message_product = product_result.get("message", {})
            response.status_code = product_result.get("status_code", 200)
            return convert_case(message_product, 'camel')
        raise HTTPException(status_code=product_result.get("status_code", 500),
                            detail={"error": product_result.get("error", "Something went wrong")})


@router.get("/get_main_menu/", tags=['Product'])
def get_main_menu(
        response: Response,
        customer_type: str = Query("B2B"),
        access: Optional[str] = Header(None),
        refresh: Optional[str] = Header(None),
):
    allowed_storages = []
    if access or refresh:
        user_data, tokens = auth_handler.check_current_user_tokens(access, refresh)
        customer_type = user_data.get("customer_type", ["B2B"])[0]
        customer_type = customer_type if not customer_type == "B2B2C" else "B2B"
        allowed_storages = get_allowed_storages(user_data.get("user_id"))

    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        product_result = rpc.publish(
            message={
                "product": {
                    "action": "get_main_menu",
                    "body": {
                        "customer_type": customer_type,
                        "user_allowed_storages": allowed_storages
                    }
                }
            },
            headers={'product': True}
        )
        product_result = product_result.get("product", {})
        if product_result.get("success"):
            message_product = product_result.get("message", {})
            response.status_code = product_result.get("status_code", 200)
            return convert_case(message_product, 'camel')
        raise HTTPException(status_code=product_result.get("status_code", 500),
                            detail={"error": product_result.get("error", "Something went wrong")})
