from typing import Optional, List

from fastapi import HTTPException, APIRouter, Response, Query

from source.helpers.case_converter import convert_case
from source.message_broker.rabbit_server import RabbitRPC
from source.routers.customer.module.auth import AuthHandler
from source.routers.product.validators.product import KowsarCustomCategory, \
    CustomCategory

router = APIRouter()

auth_handler = AuthHandler()


@router.get("/categories/", tags=["Custom Category"])
def get_all_categories(
        response: Response
):
    """
    Get all available categories in database.
    """
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        product_result = rpc.publish(
            message={
                "product": {
                    "action": "get_all_categories",
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


@router.post("/custom_kowsar_categories/", tags=["Custom Category"])
def create_custom_kowsar_category(
        response: Response,
        custom_category: KowsarCustomCategory
):
    """
    Can be used to give custome name and visibility to main categories (2 digits)
    Can be used to give custome name and visibility to sub categories (4 digits)
    Can be used to give custome name and visibility to brands (6 digits)
    """
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        product_result = rpc.publish(
            message={
                "product": {
                    "action": "create_custom_kowsar_category",
                    "body": dict(custom_category)
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


@router.post("/custom_categories/", tags=["Custom Category"])
def create_custom_category(
        response: Response,
        custom_category: CustomCategory
):
    """
    Create a custom category for 2 digits, until 12 digits.
    """
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        product_result = rpc.publish(
            message={
                "product": {
                    "action": "create_custom_category",
                    "body": dict(custom_category)
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


@router.get("/get_custom_category_list/", tags=["Custom Category"])
def get_custom_category_list(
        response: Response,
        visible_in_site: Optional[bool] = Query(None, alias="visibleInSite"),
        created_at_from: Optional[str] = Query(None, alias="createdAtFrom"),
        created_at_to: Optional[str] = Query(None, alias="createdAtTo"),
        page: Optional[int] = Query(1),
        per_page: Optional[int] = Query(15)
):
    """
    get custom category list
    """
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        product_result = rpc.publish(
            message={
                "product": {
                    "action": "get_custom_category_list",
                    "body": {
                        "visible_in_site": visible_in_site,
                        "created_at_from": created_at_from,
                        "created_at_to": created_at_to,
                        "page": page,
                        "per_page": per_page
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


@router.delete("/custom_categories/{name}", tags=["Custom Category"])
def delete_custom_category(
        response: Response,
        name: str,
):
    """
    delete custom category
    """
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        product_result = rpc.publish(
            message={
                "product": {
                    "action": "delete_custom_category",
                    "body": {
                        "name": name
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


@router.put("/custom_categories/{name}", tags=["Custom Category"])
def edit_custom_category(
        response: Response,
        name: str,
        new_name: Optional[str] = Query(None, alias="newName"),
        products: Optional[List[str]] = Query(None, alias="products"),
        visible_in_site: Optional[bool] = Query(None, alias="visibleInSite"),
        image: Optional[str] = Query(None, alias="image")

):
    """
    edit custom category
    """
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        product_result = rpc.publish(
            message={
                "product": {
                    "action": "edit_custom_category",
                    "body": {
                        "name": name,
                        "new_name": new_name,
                        "products": products,
                        "visible_in_site": visible_in_site,
                        "image": image
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


@router.get("/categories_products/", tags=["Custom Category"])
def get_categories_products(
        response: Response,
        system_code: str = Query(None, alias="systemCode"),
        page: int = Query(1, alias="page"),
        per_page: int = Query(20, alias="perPage")
):
    """
    Get products of a category
    """
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        product_result = rpc.publish(
            message={
                "product": {
                    "action": "get_categories_products",
                    "body": {
                        "system_code": system_code,
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
