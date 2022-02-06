from fastapi import FastAPI, HTTPException, Response, responses, Path, Body, Query
from starlette.exceptions import HTTPException as starletteHTTPException

from source.routers.product.validators import CreateParent
from source.config import settings
from source.message_broker.rabbit_server import RabbitRPC

# from source.routers.quantity.validators.quantity import Quantity
from source.routers.product.validators.product import CreateChild, AddAtributes

TAGS = [
    {
        "name": "Product",
        "description": "Product CRUD"
    }
]
app = FastAPI(
    title="Product API",
    description="This is Product gateway MicroService",
    version="0.1.0",
    openapi_tags=TAGS,
    docs_url="/api/v1/docs/",
    redoc_url="/api/v1/redoc/",
    debug=settings.DEBUG_MODE
)


@app.exception_handler(starletteHTTPException)
def validation_exception_handler(request, exc):
    return responses.JSONResponse(exc.detail, status_code=exc.status_code)


rpc = RabbitRPC(exchange_name='headers_exchange', timeout=5)
rpc.connect()
rpc.consume()


@app.get("/api/v1/product/parent/{system_code}/configs/", tags=["Product"])
def get_parent_configs(system_code: str, response: Response) -> dict:
    rpc.response_len_setter(response_len=1)
    product_result = rpc.publish(
        message={
            "product": {
                "action": "get_parent_configs",
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
        return product_result.get("message")
    raise HTTPException(status_code=product_result.get("status_code", 500),
                        detail={"error": product_result.get("error", "Something went wrong")})


@app.get("/product/parent/", status_code=200)
def create_parent_schema():
    return CreateParent.schema().get("properties")


@app.post("/product/parent/", status_code=201)
def create_parent(
        item: CreateParent, response: Response
) -> dict:
    rpc.response_len_setter(response_len=1)
    product_result = rpc.publish(
        message={
            "product": {
                "action": "create_parent",
                "body": dict(item)
            }
        },
        headers={'product': True}
    )
    product_result = product_result.get("product", {})
    if product_result.get("success"):
        response.status_code = product_result.get("status_code", 200)
        return product_result.get("message")
    raise HTTPException(status_code=product_result.get("status_code", 500),
                        detail={"error": product_result.get("error", "Something went wrong")})


@app.get("/product/{system_code}/items", status_code=200)
def suggest_product(response: Response, system_code: str = Path(..., min_length=11, max_length=11)) -> dict:
    rpc.response_len_setter(response_len=1)
    product_result = rpc.publish(
        message={
            "product": {
                "action": "suggest_product",
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
        return product_result.get("message")
    raise HTTPException(status_code=product_result.get("status_code", 500),
                        detail={"error": product_result.get("error", "Something went wrong")})


@app.get("/product/child/", status_code=200)
def create_child_schema():
    return CreateChild.schema().get("properties")


@app.post("/product/child/", status_code=201)
def create_child(
        item: CreateChild, response: Response
) -> dict:
    """
    Create a product for sale in main collection in database.
    attributes will be validated before insert.
    """
    rpc.response_len_setter(response_len=1)
    product_result = rpc.publish(
        message={
            "product": {
                "action": "create_child",
                "body": dict(item)
            }
        },
        headers={'product': True}
    )
    product_result = product_result.get("product", {})
    if product_result.get("success"):
        response.status_code = product_result.get("status_code", 200)
        return product_result.get("message")
    raise HTTPException(status_code=product_result.get("status_code", 500),
                        detail={"error": product_result.get("error", "Something went wrong")})


@app.get("/product/attributes/", status_code=200)
def add_attributes_schema():
    return AddAtributes.schema().get("properties")


@app.post("/product/attributes/", status_code=201)
def add_attributes(response: Response,
                   item: AddAtributes = Body(..., example={
                       "system_code": "100104021006",
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
    rpc.response_len_setter(response_len=1)
    product_result = rpc.publish(
        message={
            "product": {
                "action": "add_attributes",
                "body": dict(item)
            }
        },
        headers={'product': True}
    )
    product_result = product_result.get("product", {})
    if product_result.get("success"):
        response.status_code = product_result.get("status_code", 200)
        return product_result.get("message")
    raise HTTPException(status_code=product_result.get("status_code", 500),
                        detail={"error": product_result.get("error", "Something went wrong")})


@app.get("/product/{system_code}/{lang}", status_code=200)
def get_product_by_system_code(
        response: Response,
        system_code: str = Path(..., min_length=11, max_length=11),
        lang: str = Path("fa_ir", min_length=2, max_length=127)
) -> dict:
    """
    Get a product by system_code in main collection in database.
    """
    rpc.response_len_setter(response_len=1)
    product_result = rpc.publish(
        message={
            "product": {
                "action": "get_product_by_system_code",
                "body": {
                    "system_code": system_code,
                    "lang": lang
                }
            }
        },
        headers={'product': True}
    )
    product_result = product_result.get("product", {})
    if product_result.get("success"):
        response.status_code = product_result.get("status_code", 200)
        return product_result.get("message")
    raise HTTPException(status_code=product_result.get("status_code", 500),
                        detail={"error": product_result.get("error", "Something went wrong")})


@app.delete("/product/{system_code}", status_code=200)
def delete_product(
        response: Response,
        system_code: str = Path(..., min_length=3, max_length=255)
) -> dict:
    """
    Delete a product by name in main collection in database.
    """
    rpc.response_len_setter(response_len=1)
    product_result = rpc.publish(
        message={
            "product": {
                "action": "delete_product",
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
        return product_result.get("message")
    raise HTTPException(status_code=product_result.get("status_code", 500),
                        detail={"error": product_result.get("error", "Something went wrong")})


@app.get("/product/update_attribute_collection/", status_code=200)
def update_attribute_collection(response: Response) -> dict:
    """
    Update the attribute collection in database.
    """
    # TODO: Later, the attributes below should come from API GW
    attributes = [
        {
            "required": True,
            "use_in_filter": False,
            "use_for_sort": False,
            "default_value": None,
            "values": None,
            "set_to_nodes": False,
            "name": "year",
            "label": "سال",
            "input_type": "Number",
            "parent": "100104021006"
        },
        {
            "required": False,
            "use_in_filter": False,
            "use_for_sort": False,
            "default_value": "/src/default.png",
            "values": None,
            "set_to_nodes": True,
            "name": "image",
            "label": "عکس",
            "input_type": "Media Image",
            "parent": "1001"
        }
    ]
    rpc.response_len_setter(response_len=1)
    product_result = rpc.publish(
        message={
            "product": {
                "action": "update_attribute_collection",
                "body": {
                    "attributes": attributes
                }
            }
        },
        headers={'product': True}
    )
    product_result = product_result.get("product", {})
    if product_result.get("success"):
        response.status_code = product_result.get("status_code", 200)
        return product_result.get("message")
    raise HTTPException(status_code=product_result.get("status_code", 500),
                        detail={"error": product_result.get("error", "Something went wrong")})


@app.get("/categories/{system_code}/")
def get_all_categories(
                       response: Response,
                       system_code: str = Path(00, min_length=2, max_length=6),
                       page: int = Query(1, ge=1, le=1000),
                       per_page: int = Query(15, ge=1, le=1000)):
    """
    """
    rpc.response_len_setter(response_len=1)
    product_result = rpc.publish(
        message={
            "product": {
                "action": "get_all_categories",
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
        response.status_code = product_result.get("status_code", 200)
        return product_result.get("message")
    raise HTTPException(status_code=product_result.get("status_code", 500),
                        detail={"error": product_result.get("error", "Something went wrong")})

#
# @app.post("/api/v1/product/quantity/", tags=["Quantity"])
# def set_product_quantity(item: Quantity, response: Response) -> dict:
#     rpc.response_len_setter(response_len=1)
#     quantity_result = rpc.publish(
#         message={
#             "quantity": {
#                 "action": "set_quantity",
#                 "body": item.get()
#             }
#         },
#         headers={'quantity': True}
#     )
#     quantity_result = quantity_result.get("quantity", {})
#     if quantity_result.get("success"):
#         response.status_code = quantity_result.get("status_code", 200)
#         return quantity_result.get("message")
#     raise HTTPException(status_code=quantity_result.get("status_code", 500),
#                         detail={"error": quantity_result.get("error", "Something went wrong")})
#
#
# @app.get("/api/v1/product/quantity/{system_code}/", tags=["Quantity"])
# def get_product_quantity(system_code: str, response: Response) -> dict:
#     rpc.response_len_setter(response_len=1)
#     quantity_result = rpc.publish(
#         message={
#             "quantity": {
#                 "action": "get_quantity",
#                 "body": {
#                     "system_code": system_code
#                 }
#             }
#         },
#         headers={'quantity': True}
#     )
#     quantity_result = quantity_result.get("quantity", {})
#     if quantity_result.get("success"):
#         response.status_code = quantity_result.get("status_code", 200)
#         return quantity_result.get("message")
#     raise HTTPException(status_code=quantity_result.get("status_code", 500),
#                         detail={"error": quantity_result.get("error", "Something went wrong")})
#
#
# @app.get("/api/v1/product/stock/", tags=["Quantity"])
# def get_product_stock(system_code: str, response: Response) -> dict:
#     rpc.response_len_setter(response_len=1)
#     quantity_result = rpc.publish(
#         message={
#             "quantity": {
#                 "action": "get_stock",
#                 "body": {
#                     "system_code": system_code
#                 }
#             }
#         },
#         headers={'quantity': True}
#     )
#     quantity_result = quantity_result.get("quantity", {})
#     if quantity_result.get("success"):
#         response.status_code = quantity_result.get("status_code", 200)
#         return quantity_result.get("message")
#     raise HTTPException(status_code=quantity_result.get("status_code", 500),
#                         detail={"error": quantity_result.get("error", "Something went wrong")})
