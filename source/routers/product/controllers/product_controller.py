from typing import Optional, List

from fastapi import HTTPException, APIRouter, Response, Path, Body, Query, Header

from source.helpers.case_converter import convert_case
from source.helpers.create_class import CreateClass
from source.message_broker.rabbit_server import RabbitRPC
from source.routers.customer.module.auth import AuthHandler
from source.routers.product.modules.allowed_storages import get_allowed_storages
from source.routers.product.validators.price_models import Price
from source.routers.product.validators.price_models import UpdatePrice
from source.routers.product.validators.product import Product, AddAttributes, EditProduct
from source.routers.product.validators.quantity_models import UpdateQuantity, Quantity
from source.message_broker.rabbitmq import new_rpc

router = APIRouter()

auth_handler = AuthHandler()


@router.post("/product/create_product/", tags=["Product"])
def create_product(
        response: Response,
        item: Product
):
    """
    Create product
    """
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        product_result = rpc.publish(
            message={
                "product": {
                    "action": "create_product",
                    "body": {
                        "name": item.name,
                        "url_name": item.url_name,
                        "system_codes": item.system_codes,
                    }
                }
            },
            headers={'product': True}
        )
        product_result = product_result.get("product", {})
        if product_result.get("success"):
            response.status_code = product_result.get("status_code", 200)
            return convert_case({"message": product_result.get("message")}, 'camel')
        raise HTTPException(status_code=product_result.get("status_code", 500),
                            detail={"error": product_result.get("error", "Something went wrong")})


@router.get("/product/get_product_attributes/{systemCode}/", tags=["Product"])
def get_product_attributes(response: Response,
                           system_code: str = Path(..., min_length=25, max_length=25, alias='systemCode')) -> dict:
    """
    Get product attributes
    """
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        product_attrs_result = rpc.publish(
            message={
                "product": {
                    "action": "get_product_attributes",
                    "body": {
                        "system_code": system_code
                    }
                }
            },
            headers={'product': True}
        )
        product_attrs_result = product_attrs_result.get("product", {})
        if product_attrs_result.get("success"):
            response.status_code = product_attrs_result.get("status_code", 200)
            return convert_case(product_attrs_result.get("message", {}), 'camel')
        raise HTTPException(status_code=product_attrs_result.get("status_code", 500),
                            detail={"error": product_attrs_result.get("error", "Something went wrong")})


@router.post("/product/add_attributes/", tags=["Product"])
def add_attributes(response: Response,
                   item: AddAttributes = Body(..., example={
                       "systemCode": "100104021006",
                       "attributes": {
                           "image": "/src/default.jpg",
                           "year": 2020
                       }
                   })
                   ) -> dict:
    """
    Create a product for sale in main collection in database.
    attributes will be validated before insert.
    """
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        attribute_result = rpc.publish(
            message={
                "product": {
                    "action": "get_product_attributes",
                    "body": {
                        "system_code": item.system_code
                    }
                }
            },
            headers={'product': True}
        )
        attributes = attribute_result.get("product", {}).get("message", {}).get("attributes", {})
        dict_data = {obj.get("name"): obj for obj in attributes}
        attribute_model = CreateClass(class_name="attribute_model", attributes=dict_data).get_pydantic_class()
        attribute_object = attribute_model(**item.attributes)
        product_result = rpc.publish(
            message={
                "product": {
                    "action": "add_attributes",
                    "body": {
                        "system_code": item.system_code,
                        "attributes": dict(attribute_object)
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


@router.get("/product/get_backoffice/", tags=["Product"])
def get_product_backoffice(system_code: str = Query(..., min_length=25, max_length=25, alias='systemCode')) -> dict:
    """
    Get product backoffice
    """
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        product_result = rpc.publish(
            message={
                "product": {
                    "action": "get_product_backoffice",
                    "body": {
                        "system_code": system_code
                    }
                }
            },
            headers={'product': True}
        )
        product_result = product_result.get("product", {})
        if product_result.get("success"):
            return convert_case(product_result.get("message"), 'camel')
        raise HTTPException(status_code=product_result.get("status_code", 500),
                            detail={"error": product_result.get("error", "Something went wrong")})


@router.post("/product/price/", tags=["Product"])
def set_product_price(item: Price, response: Response) -> dict:
    """
    set product(12 digits) price according to customer type and warehouse
    priority of each price is like this:
    1. Special price of warehouse
    2. Price of warehouse
    3. Special price of customer type
    4. Price of customer type
    5. Special price of all
    6. Price of all
    """
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        product_result = rpc.publish(
            message={
                "product": {
                    "action": "set_product_price",
                    "body": item.get()
                }
            },
            headers={'product': True}
        )
        pricing_result = product_result.get("product", {})
        if pricing_result.get("success"):
            response.status_code = pricing_result.get("status_code", 200)
            return {"message": pricing_result.get("message")}
        raise HTTPException(status_code=pricing_result.get("status_code", 500),
                            detail={"error": pricing_result.get("error", "Something went wrong")})


@router.put("/product/price/", tags=["Product"])
def update_product_price(item: UpdatePrice, response: Response) -> dict:
    """
    update product(12 digits) price according to customer type and warehouse
    priority of each price is like this:
    1. Special price of warehouse
    2. Price of warehouse
    3. Special price of customer type
    4. Price of customer type
    5. Special price of all
    6. Price of all
    """
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        pricing_result = rpc.publish(
            message={
                "product": {
                    "action": "update_price",
                    "body": item.__dict__
                }
            },
            headers={'product': True}
        )
        rpc.publish(
            message={
                "dealership": {
                    "action": "update_product",
                    "body": item.__dict__
                }
            },
            headers={'dealership': True}
        )
        pricing_result = pricing_result.get("product", {})
        if pricing_result.get("success"):
            response.status_code = pricing_result.get("status_code", 200)
            return {"message": pricing_result.get("message")}
        raise HTTPException(status_code=pricing_result.get("status_code", 500),
                            detail={"error": pricing_result.get("error", "Something went wrong")})


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


@router.post("/product/quantity/", tags=["Product"])
def set_product_quantity(item: Quantity, response: Response) -> dict:
    """
    set product(12 digits) quantity according to customer type and warehouse
    priority of each quantity is like this:
    1. Stock for sale of warehouse
    2. Stock for sale of customer type
    3. Stock for sale of all
    """
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        quantity_result = rpc.publish(
            message={
                "product": {
                    "action": "set_product_quantity",
                    "body": item.get()
                }
            },
            headers={'product': True}
        )
        quantity_result = quantity_result.get("product", {})
        if quantity_result.get("success"):
            response.status_code = quantity_result.get("status_code", 200)
            return {"message": quantity_result.get("message")}
        raise HTTPException(status_code=quantity_result.get("status_code", 500),
                            detail={"error": quantity_result.get("error", "Something went wrong")})


@router.put("/product/quantity/", tags=["Product"])
def update_product_quantity(item: UpdateQuantity, response: Response) -> dict:
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        quantity_result = rpc.publish(
            message={
                "product": {
                    "action": "update_quantity",
                    "body": item.__dict__
                }
            },
            headers={'product': True}
        )
        quantity_result = quantity_result.get("product", {})
        if quantity_result.get("success"):
            response.status_code = quantity_result.get("status_code", 200)
            return {"message": quantity_result.get("message")}
        raise HTTPException(status_code=quantity_result.get("status_code", 500),
                            detail={"error": quantity_result.get("error", "Something went wrong")})


@router.post("/product/edit_product/{systemCode}", tags=["Product"])
def edit_product(
        response: Response,
        system_code: str = Path(..., min_length=25, max_length=25, alias='systemCode'),
        item: EditProduct = Body(...)
) -> dict:
    """
    Edit a product by name in main collection in database.
    """
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        product_result = rpc.publish(
            message={
                "product": {
                    "action": "edit_product",
                    "body": {
                        "system_code": system_code,
                        "item": dict(item)
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


@router.get("/product/get_product_list_back_office/", tags=["Product"])
def get_product_list_back_office(
        response: Response,
        brands: Optional[List[str]] = Query(None),
        warehouses: Optional[List[str]] = Query(None),
        price_from: Optional[int] = Query(None),
        price_to: Optional[int] = Query(None),
        sellers: Optional[List[str]] = Query(None),
        colors: Optional[List[str]] = Query(None),
        quantity_from: Optional[int] = Query(None),
        quantity_to: Optional[int] = Query(None),
        date_from: Optional[str] = Query(None),
        date_to: Optional[str] = Query(None),
        guarantees: Optional[List[str]] = Query(None),
        steps: Optional[List[int]] = Query(None),
        visible_in_site: Optional[bool] = Query(None, alias='visibleInSite'),
        approved: Optional[bool] = Query(None),
        available: Optional[bool] = Query(None),
        page: Optional[int] = Query(1),
        per_page: Optional[int] = Query(15),
        system_code: Optional[str] = Query(None),
        lang: Optional[str] = Query("fa_ir")
):
    """
    Get product list in  back office
    """
    product_result = new_rpc.publish(
        message=[{
            "product": {
                "action": "get_product_list_back_office",
                "body": {
                    "brands": brands,
                    "warehouses": warehouses,
                    "price_from": price_from,
                    "price_to": price_to,
                    "sellers": sellers,
                    "colors": colors,
                    "quantity_from": quantity_from,
                    "quantity_to": quantity_to,
                    "date_from": date_from,
                    "date_to": date_to,
                    "guarantees": guarantees,
                    "steps": steps,
                    "visible_in_site": visible_in_site,
                    "approved": approved,
                    "available": available,
                    "page": page,
                    "per_page": per_page,
                    "system_code": system_code,
                    "lang": lang
                }
            }
        }]
    )
    if product_result.get("success"):
        response.status_code = product_result.get("status_code", 200)
        return convert_case(product_result.get("message"), 'camel')
    raise HTTPException(status_code=product_result.get("status_code", 500),
                        detail={"error": product_result.get("error", "Something went wrong")})


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
    if access or refresh:
        user_data, tokens = auth_handler.check_current_user_tokens(access, refresh)
        customer_type = user_data.get("customer_type", ["B2B"])[0]
        allowed_storages = get_allowed_storages(user_data.get("user_id"))

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
                        "lang": lang
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
        customer_type: str = Query("B2B"),
        page: int = Query(None),
        per_page: int = Query(None)
):
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        product_result = rpc.publish(
            message={
                "product": {
                    "action": "get_data_price_list_pic",
                    "body": {
                        "customer_type": customer_type,
                        "page": page,
                        "per_page": per_page
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
