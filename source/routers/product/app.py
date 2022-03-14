from typing import Optional, List, Tuple

from fastapi import FastAPI, HTTPException, Response, responses, Path, Body, Query, Depends, Header
from starlette.exceptions import HTTPException as starletteHTTPException

from source.config import settings
from source.helpers.case_converter import convert_case
from source.message_broker.rabbit_server import RabbitRPC
from source.routers.customer.module.auth import AuthHandler
from source.routers.product.validators.product import CreateChild, AddAtributes, CreateParent
from source.helpers.create_class import CreateClass

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
    docs_url="/docs/",
    redoc_url="/redoc/",
    debug=settings.DEBUG_MODE
)


# customize exception handler of fast api
@app.exception_handler(starletteHTTPException)
def validation_exception_handler(request, exc):
    return responses.JSONResponse(exc.detail, status_code=exc.status_code)


# initialize rabbit mq
rpc = RabbitRPC(exchange_name='headers_exchange', timeout=5)
rpc.connect()
rpc.consume()

auth_handler = AuthHandler()


@app.get("/parent/{systemCode}/configs/", tags=["Product"])
def get_parent_configs(response: Response,
                       system_code: str = Path(..., min_length=9, max_length=9, alias='systemCode')) -> dict:
    """
    Get parent system code configs
    """
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
        return convert_case(product_result.get("message"), 'camel')
    raise HTTPException(status_code=product_result.get("status_code", 500),
                        detail={"error": product_result.get("error", "Something went wrong")})


@app.get("/parent/", tags=["Product"])
def create_parent_schema():
    """
    Get create parent json schema
    """
    return CreateParent.schema().get("properties")


@app.post("/parent/", tags=["Product"])
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
        return convert_case(product_result.get("message"), 'camel')
    raise HTTPException(status_code=product_result.get("status_code", 500),
                        detail={"error": product_result.get("error", "Something went wrong")})


@app.get("/{systemCode}/items", tags=["Product"])
def suggest_product(response: Response,
                    system_code: str = Path(..., min_length=11, max_length=11, alias='systemCode')) -> dict:
    """
    Get child system code configs
    """
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
        return convert_case(product_result.get("message"), 'camel')
    raise HTTPException(status_code=product_result.get("status_code", 500),
                        detail={"error": product_result.get("error", "Something went wrong")})


@app.get("/child/", tags=["Product"])
def create_child_schema():
    """
    Get create child json schema
    """
    return CreateChild.schema().get("properties")


@app.post("/child/", tags=["Product"])
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
        return convert_case(product_result.get("message"), 'camel')
    raise HTTPException(status_code=product_result.get("status_code", 500),
                        detail={"error": product_result.get("error", "Something went wrong")})


@app.get("/get_product_attributes/{systemCode}/", tags=["Product"])
def get_product_attributes(response: Response,
                           system_code: str = Path(..., min_length=12, max_length=12, alias='systemCode')) -> dict:
    """
    Get product attributes
    """
    rpc.response_len_setter(response_len=1)
    product_result = rpc.publish(
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
    product_result = product_result.get("product", {})
    if product_result.get("success"):
        response.status_code = product_result.get("status_code", 200)
        return convert_case(product_result.get("message"), 'camel')
    raise HTTPException(status_code=product_result.get("status_code", 500),
                        detail={"error": product_result.get("error", "Something went wrong")})


@app.get("/attributes/", tags=["Product"])
def add_attributes_schema():
    """
    Get add attributes json schema
    """
    return AddAtributes.schema().get("properties")


@app.post("/attributes/", tags=["Product"])
def add_attributes(response: Response,
                   item: AddAtributes = Body(..., example={
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
    rpc.response_len_setter(response_len=1)
    attribute_result = rpc.publish(
        message={
            "product": {
                "action": "get_kowsar",
                "body": {
                    "system_code": item.system_code,
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


@app.get("/{systemCode}/{lang}", tags=["Product"])
def get_product_by_system_code(
        response: Response,
        system_code: str = Path(..., min_length=11, max_length=11, alias='systemCode'),
        lang: str = Path("fa_ir", min_length=2, max_length=8),
        access_token: Optional[str] = Header(None),
        refresh_token: Optional[str] = Header(None)
) -> dict:
    """
    Get a product by system_code in main collection in database.
    """
    customer_type = "B2B"
    if access_token or refresh_token:
        user_data, tokens = auth_handler.check_current_user_tokens(access_token, refresh_token)
        customer_type = user_data.get("customer_type", "B2B")
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
            for quantity_key, quantity in quantity_result.get("message", {}).get("products", {}).get(
                    product.get("system_code")).get("customer_types").get(customer_type).get("storages", {}).items():

                for price_key, price in pricing_result.get("message", {}).get("products", {}).get(
                        product.get("system_code")).get("customer_type").get(customer_type).get("storages", {}).items():

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
        return convert_case(final_result, 'camel')


@app.delete("/{systemCode}", tags=["Product"])
def delete_product(
        response: Response,
        system_code: str = Path(..., min_length=12, max_length=12, alias='systemCode')
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
        return convert_case(product_result.get("message"), 'camel')
    raise HTTPException(status_code=product_result.get("status_code", 500),
                        detail={"error": product_result.get("error", "Something went wrong")})


@app.get("/update_attribute_collection/", tags=["Product"])
def update_attribute_collection(response: Response) -> dict:
    """
    Update the attribute collection in database.
    """
    # TODO: Later, it should be moved to add attribute from attribute service
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
        return convert_case(product_result.get("message"), 'camel')
    raise HTTPException(status_code=product_result.get("status_code", 500),
                        detail={"error": product_result.get("error", "Something went wrong")})


@app.get("/categories/{systemCode}/", tags=["Product"])
def get_all_categories(
        response: Response,
        system_code: str = Path(00, min_length=2, max_length=6, alias='systemCode'),
        page: int = Query(1, ge=1, le=1000),
        per_page: int = Query(15, ge=1, le=1000, alias='perPage')):
    """
    Get all available categories in database.
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
        return convert_case(product_result.get("message"), 'camel')
    raise HTTPException(status_code=product_result.get("status_code", 500),
                        detail={"error": product_result.get("error", "Something went wrong")})


@app.get("/{systemCode}/", tags=["Kowsar"])
def get_kowsar(
        response: Response,
        system_code: str = Path(..., min_length=2, max_length=12, alias='systemCode')
):
    """
    Get kowsar item by system code
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
        return convert_case(product_result.get("message"), 'camel')
    raise HTTPException(status_code=product_result.get("status_code", 500),
                        detail={"error": product_result.get("error", "Something went wrong")})


@app.get("/{systemCode}/items/", tags=["Kowsar"])
def get_kowsar_items(
        response: Response,
        system_code: str = Path(..., min_length=2, max_length=9, alias='systemCode')
):
    """
    Get children of kowsar item
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
        return convert_case(product_result.get("message"), 'camel')
    raise HTTPException(status_code=product_result.get("status_code", 500),
                        detail={"error": product_result.get("error", "Something went wrong")})


@app.get("/update_collection", tags=["Kowsar"])
def update_kowsar_collection(
        response: Response
):
    """
    Update kowsar collection based on given file
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
        return convert_case(product_result.get("message"), 'camel')
    raise HTTPException(status_code=product_result.get("status_code", 500),
                        detail={"error": product_result.get("error", "Something went wrong")})


@app.get("/get_product_list_by_system_code/{systemCode}/", tags=["Product"])
def get_product_list_by_system_code(
        response: Response,
        system_code: int = Path(..., alias='systemCode'),
        page: int = Query(1, alias='page'),
        per_page: int = Query(10, alias='perPage'),
        # auth_header=Depends(auth_handler.check_current_user_tokens)

):
    """
    Get product list by brand
    """
    # customer_type = auth_header[0].get("customer_type")
    customer_type = "B2B"
    rpc.response_len_setter(response_len=1)
    product_result = rpc.publish(
        message={
            "product": {
                "action": "get_product_list_by_system_code",
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
        for product in message_product['products']:
            pricing_result = rpc.publish(
                message={
                    "pricing": {
                        "action": "get_price",
                        "body": {
                            "system_code": product.get("system_code")
                        }
                    }
                },
                headers={'pricing': True}
            )
            pricing_result = pricing_result.get("pricing", {})

            if pricing_result.get("success"):
                for system_code, prices in pricing_result.get("message", {}).get("pricing", {}).items():
                    product["price"] = prices.get("regular", 0)
                    product["special_price"] = prices.get("special", 0)
            else:
                product["price"] = 0
                product["special_price"] = 0

        response.status_code = product_result.get("status_code", 200)
        for i in message_product.keys():
            for j in message_product[i]:
                j['image'] = "default.png"
        return convert_case(message_product, 'camel')
    raise HTTPException(status_code=product_result.get("status_code", 500),
                        detail={"error": product_result.get("error", "Something went wrong")})


@app.get("/get_category_list", tags=["Product"])
def get_category_list(
        response: Response,
        # auth_header=Depends(auth_handler.check_current_user_tokens)
):
    """
    Get category list
    """
    # customer_type = auth_header[0].get("customer_type")
    customer_type = "B2B"
    rpc.response_len_setter(response_len=1)

    product_result = rpc.publish(
        message={
            "product": {
                "action": "get_category_list",
                "body": {}
            }
        },
        headers={'product': True}
    )
    product_result = product_result.get("product", {})
    if product_result.get("success"):
        message_product = product_result.get("message", {})
        product_list = list()
        for key in message_product.keys():
            if key != "latest_product":
                for obj in message_product[key]['items']:
                    obj['image'] = "default.png"
        for product in message_product['product']['items']:
            product['image'] = "/default_product.png"
            pricing_result = rpc.publish(
                message={
                    "pricing": {
                        "action": "get_price",
                        "body": {
                            "system_code": product.get("system_code")
                        }
                    }
                },
                headers={'pricing': True}
            )
            pricing_result = pricing_result.get("pricing", {})
            price_tuples = list()
            if pricing_result.get("success"):
                for system_code, prices in pricing_result.get("message", {}).get("products", {}).items():
                    customer_type_price = prices.get("customer_type", {}).get(customer_type, {})
                    price_tuples.append((customer_type_price.get("regular"), customer_type_price.get("special")))
                    for storage, storage_prices in prices.get("storages", {}).items():
                        price_tuples.append((storage_prices.get("regular"), storage_prices.get("special")))

                price_tuples.sort(key=lambda x: x[1])
                price, special_price = (None, None)
                if price_tuples:
                    price, special_price = price_tuples[0]
                product["price"] = price
                product["special_price"] = special_price
                product_list.append(product)
        message_product['product']['items'] = product_list
        response.status_code = product_result.get("status_code", 200)
        return convert_case(message_product, 'camel')
    raise HTTPException(status_code=product_result.get("status_code", 500),
                        detail={"error": product_result.get("error", "Something went wrong")})

#
# @app.get("/get_product_list_back_office", tags=["Product"])
# def get_product_list_back_office(
#         response: Response,
#         brands: Optional[List[str]] = Query(None),
#         warehouses: Optional[List[str]] = Query(None),
#         price: Optional[Tuple[str, str]] = Query(None),
#         sellers: Optional[List[str]] = Query(None),
#         colors: Optional[List[str]] = Query(None),
#         quantity: Optional[Tuple[str, str]] = Query(None),
#         date: Optional[Tuple[str, str]] = Query(None),
#         guarantees: Optional[List[str]] = Query(None),
#         steps: Optional[List[str]] = Query(None),
#         visible_in_site: Optional[bool] = Query(None, alias='visibleInSite'),
#         approved: Optional[bool] = Query(None),
#         available: Optional[bool] = Query(None),
#         page: Optional[int] = Query(1),
#         per_page: Optional[int] = Query(15),
#         # auth_header=Depends(auth_handler.check_current_user_tokens)
# ):
#     """
#     Get product list
#     """
#     # customer_type = auth_header[0].get("customer_type")
#     customer_type = "B2B"
#     rpc.response_len_setter(response_len=1)
#     product_result = rpc.publish(
#         message={
#             "producttt": {
#                 "action": "get_product_list_back_office",
#                 "body": {
#                     "brands": brands,
#                     "warehouses": warehouses,
#                     "price": price,
#                     "sellers": sellers,
#                     "colors": colors,
#                     "quantity": quantity,
#                     "date": date,
#                     "guarantees": guarantees,
#                     "steps": steps,
#                     "visible_in_site": visible_in_site,
#                     "approved": approved,
#                     "available": available,
#                     "page": page,
#                     "per_page": per_page,
#                 }
#             }
#         },
#         headers={'producttt': True}
#     )
#     product_result = product_result.get("producttt", {})
#     message_product = product_result.get("message", {})
#     product_list = list()
#     for product in message_product['products']:
#         product['image'] = "/default_product.png"
#         pricing_result = rpc.publish(
#             message={
#                 "pricing": {
#                     "action": "get_price",
#                     "body": {
#                         "system_code": product.get("system_code")
#                     }
#                 }
#             },
#             headers={'pricing': True}
#         )
#         pricing_result = pricing_result.get("pricing", {})
#         price_tuples = list()
#         if pricing_result.get("success"):
#             for system_code, prices in pricing_result.get("message", {}).get("products", {}).items():
#                 customer_type_price = prices.get("customer_type", {}).get(customer_type, {})
#                 price_tuples.append((customer_type_price.get("regular"), customer_type_price.get("special")))
#                 for storage, storage_prices in prices.get("storages", {}).items():
#                     price_tuples.append((storage_prices.get("regular"), storage_prices.get("special")))
#
#                 price_tuples.sort(key=lambda x: x[1])
#                 price, special_price = (None, None)
#                 if price_tuples:
#                     price, special_price = price_tuples[0]
#                 product["price"] = price
#                 product["special_price"] = special_price
#                 product_list.append(product)
#         message_product['latest_product'] = product_list
#     if product_result.get("success"):
#         response.status_code = product_result.get("status_code", 200)
#         return convert_case(message_product, 'camel')
#     raise HTTPException(status_code=product_result.get("status_code", 500),
#                         detail={"error": product_result.get("error", "Something went wrong")})
