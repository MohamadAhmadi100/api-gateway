from fastapi import FastAPI, HTTPException, Response, responses, Path, Body, Query
from starlette.exceptions import HTTPException as starletteHTTPException

from source.config import settings
from source.message_broker.rabbit_server import RabbitRPC
from source.routers.product.validators.product import CreateChild, AddAtributes, CreateParent

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


@app.get("/product/parent/", tags=["Product"])
def create_parent_schema():
    return CreateParent.schema().get("properties")


@app.post("/product/parent/", tags=["Product"])
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


@app.get("/product/{system_code}/items", tags=["Product"])
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


@app.get("/product/child/", tags=["Product"])
def create_child_schema():
    return CreateChild.schema().get("properties")


@app.post("/product/child/", tags=["Product"])
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


@app.get("/product/attributes/", tags=["Product"])
def add_attributes_schema():
    return AddAtributes.schema().get("properties")


@app.post("/product/attributes/", tags=["Product"])
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


@app.get("/product/{system_code}/{lang}", tags=["Product"])
def get_product_by_system_code(
        response: Response,
        system_code: str = Path(..., min_length=11, max_length=11),
        lang: str = Path("fa_ir", min_length=2, max_length=127)
) -> dict:
    """
    Get a product by system_code in main collection in database.
    """
    rpc.response_len_setter(response_len=3)
    result = rpc.publish(
        message={
            "product": {
                "action": "get_product_by_system_code",
                "body": {
                    "system_code": system_code,
                    "lang": lang
                }
            }, "pricing": {
                "action": "get_price",
                "body": {
                    "system_code": system_code
                }
            }, "quantity": {
                "action": "get_quantity",
                "body": {
                    "system_code": system_code
                }
            }
        },
        headers={'product': True, "pricing": True, "quantity": True}
    )
    product_result = result.get("product", {})
    pricing_result = result.get("pricing", {})
    quantity_result = result.get("quantity", {})
    if not product_result.get("success"):
        raise HTTPException(status_code=product_result.get("status_code", 500),
                            detail={"error": product_result.get("error", "Something went wrong")})
    elif not pricing_result.get("success"):
        raise HTTPException(status_code=pricing_result.get("status_code", 500),
                            detail={"error": pricing_result.get("error", "Something went wrong")})
    elif not quantity_result.get("success"):
        raise HTTPException(status_code=quantity_result.get("status_code", 500),
                            detail={"error": quantity_result.get("error", "Something went wrong")})
    else:
        response.status_code = product_result.get("status_code", 200)
        final_result = product_result.get("message").copy()
        for product in final_result.get("products", []):
            product["warehouse"] = list()
            for quantity in quantity_result.get("message", {}).get("products", {}).get(product.get("system_code")).get("B2B").get("storages", []):
                for price in pricing_result.get("message", {}).get("products", {}).get(product.get("system_code")).get("B2B").get("storages", []):
                    if quantity.get("storage_id") == price.get("storage_id"):
                        item = dict()
                        item["warehouse_id"] = quantity.get("storage_id")
                        item["price"] = price.get("regular")
                        item["special_price"] = price.get("special")
                        item["quantity"] = quantity.get("stock_for_sale")
                        item["warehouse_state"] = quantity.get("warehouse_state")
                        item["warehouse_city"] = quantity.get("warehouse_city")
                        item["warehouse_state_id"] = quantity.get("warehouse_state_id")
                        item["warehouse_city_id"] = quantity.get("warehouse_city_id")
                        item["warehouse_label"] = quantity.get("warehouse_label")
                        item["attribute_label"] = quantity.get("attribute_label")
                        product["warehouse"].append(item)
        return final_result


@app.delete("/product/{system_code}", tags=["Product"])
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


@app.get("/product/update_attribute_collection/", tags=["Product"])
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


@app.get("/categories/{system_code}/", tags=["Product"])
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


@app.get("/{system_code}/", tags=["Kowsar"])
def get_kowsar(
        response: Response,
        system_code: str
):
    """
    """
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
        return product_result.get("message")
    raise HTTPException(status_code=product_result.get("status_code", 500),
                        detail={"error": product_result.get("error", "Something went wrong")})


@app.get("/{system_code}/items/", tags=["Kowsar"])
def get_kowsar_items(
        response: Response,
        system_code: str
):
    """
    """
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
        return product_result.get("message")
    raise HTTPException(status_code=product_result.get("status_code", 500),
                        detail={"error": product_result.get("error", "Something went wrong")})


@app.get("/update_collection", tags=["Kowsar"])
def update_kowsar_collection(
        response: Response
):
    """
    """
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
        return product_result.get("message")
    raise HTTPException(status_code=product_result.get("status_code", 500),
                        detail={"error": product_result.get("error", "Something went wrong")})
