from typing import Optional, List

import jdatetime
from fastapi import HTTPException, Response, Path, Body, Query, Header, APIRouter

from source.helpers.case_converter import convert_case
from source.helpers.create_class import CreateClass
from source.message_broker.rabbit_server import RabbitRPC
from source.message_broker.rabbitmq import RabbitRPC as RabbitRPC_temp
from source.routers.customer.module.auth import AuthHandler
from source.routers.product.validators.product import CreateChild, AddAtributes, CreateParent, EditProduct

router = APIRouter()

auth_handler = AuthHandler()

test_rpc = RabbitRPC_temp(exchange_name="headers_exchange", timeout=15)


@router.get("/parent/{systemCode}/configs/", tags=["Product"])
def get_parent_configs(response: Response,
                       system_code: str = Path(..., min_length=9, max_length=9, alias='systemCode')) -> dict:
    """
    Get parent system code configs
    """
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        product_result = test_rpc.publish(
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


@router.post("/parent/", tags=["Product"])
def create_parent(
        item: CreateParent, response: Response
) -> dict:
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
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


@router.get("/{systemCode}/items", tags=["Product"])
def suggest_product(response: Response,
                    system_code: str = Path(..., min_length=11, max_length=11, alias='systemCode')) -> dict:
    """
    Get child system code configs
    """
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
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


@router.get("/child/", tags=["Product"])
def create_child_schema():
    """
    Get create child json schema
    """
    return CreateChild.schema().get("properties")


@router.post("/child/", tags=["Product"])
def create_child(
        item: CreateChild, response: Response
) -> dict:
    """
    Create a product for sale in main collection in database.
    attributes will be validated before insert.
    """
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
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


@router.get("/get_product_attributes/{systemCode}/", tags=["Product"])
def get_product_attributes(response: Response,
                           system_code: str = Path(..., min_length=12, max_length=12, alias='systemCode')) -> dict:
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
        product_result = rpc.publish(
            message={
                "product": {
                    "action": "get_product_child",
                    "body": {
                        "system_code": system_code,
                        "lang": "fa_ir"
                    }
                }
            },
            headers={'product': True}
        )
        product_attrs_result = product_attrs_result.get("product", {})
        product_result = product_result.get("product", {})
        if product_attrs_result.get("success"):

            for attr in product_attrs_result.get("message", {}).get("attributes", []):
                if product_result.get("message", {}).get("product", {}).get("attributes", {}).get(attr.get("name")):
                    attr["selected_value"] = product_result.get("message", {}).get("product", {}).get("attributes",
                                                                                                      {}).get(
                        attr.get("name"))
            response.status_code = product_attrs_result.get("status_code", 200)
            return convert_case(product_attrs_result.get("message", {}), 'camel')
        raise HTTPException(status_code=product_attrs_result.get("status_code", 500),
                            detail={"error": product_attrs_result.get("error", "Something went wrong")})


@router.get("/attributes/", tags=["Product"])
def add_attributes_schema():
    """
    Get add attributes json schema
    """
    return AddAtributes.schema().get("properties")


@router.post("/attributes/", tags=["Product"])
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


@router.post("/edit_product/{systemCode}", tags=["Product"])
def edit_product(
        response: Response,
        system_code: str = Path(..., min_length=11, max_length=12, alias='systemCode'),
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


@router.delete("/{systemCode}", tags=["Product"])
def delete_product(
        response: Response,
        system_code: str = Path(..., min_length=11, max_length=12, alias='systemCode')
) -> dict:
    """
    Delete a product by name in main collection in database.
    """
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
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


@router.get("/{systemCode}/{lang}", tags=["Product"])
def get_product_by_system_code(
        response: Response,
        system_code: str = Path(..., min_length=11, max_length=11, alias='systemCode'),
        lang: Optional[str] = Path("fa_ir", min_length=2, max_length=8),
        access: Optional[str] = Header(None),
        refresh: Optional[str] = Header(None)
) -> dict:
    """
    Get a product by system_code in main collection in database.
    """
    customer_type = None
    allowed_storages = list()
    if access or refresh:
        user_data, tokens = auth_handler.check_current_user_tokens(access, refresh)
        customer_type = user_data.get("customer_type", ["B2B"])[0]
        allowed_storages = user_data.get("allowed_storages", [])
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
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
            product_list = list()
            for product in final_result.get("products", []):
                if customer_type and allowed_storages:
                    product['config']["warehouse"] = list()
                    for quantity_key, quantity in quantity_result.get("message", {}).get("products", {}).get(
                            product.get("system_code"), {}).get("customer_types", {}).get(customer_type,
                                                                                          {}).get("storages",
                                                                                                  {}).items():
                        if str(quantity.get("storage_id")) in allowed_storages:

                            for price_key, price in pricing_result.get("message", {}).get("products", {}).get(
                                    product.get("system_code"), {}).get("customer_type", {}).get(customer_type,
                                                                                                 {}).get("storages",
                                                                                                         {}).items():

                                now_formated_date_time = jdatetime.datetime.strptime(
                                    jdatetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")

                                special_price_stored_date = price.get("special_to_date") if price.get(
                                    "special_to_date") else jdatetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                                special_formated_date_time = jdatetime.datetime.strptime(special_price_stored_date,
                                                                                         "%Y-%m-%d %H:%M:%S")

                                if price.get("special") and not (
                                        now_formated_date_time < special_formated_date_time):
                                    price["special"] = None

                                if quantity.get("storage_id") == price.get("storage_id"):

                                    now_quantity = quantity.get("stock_for_sale") - quantity.get('reserved')
                                    if quantity.get("min_qty") <= now_quantity and now_quantity > 0:
                                        item = dict()
                                        item["warehouse_id"] = quantity.get("storage_id")
                                        item["price"] = price.get("regular")
                                        item["special_price"] = price.get("special")
                                        item['max_qty'] = quantity.get("max_qty") if now_quantity > quantity.get(
                                            "max_qty") else now_quantity
                                        item['min_qty'] = quantity.get("min_qty")
                                        item["warehouse_state"] = quantity.get("warehouse_state")
                                        item["warehouse_city"] = quantity.get("warehouse_city")
                                        item["warehouse_state_id"] = quantity.get("warehouse_state_id")
                                        item["warehouse_city_id"] = quantity.get("warehouse_city_id")
                                        item["warehouse_label"] = quantity.get("warehouse_label")
                                        item["attribute_label"] = quantity.get("attribute_label")
                                        if now_quantity - quantity.get("min_qty") <= 3:
                                            item['alert'] = True
                                        product['config']["warehouse"].append(item)
                    if not product['config']["warehouse"]:
                        continue
                    product_list.append(product)
                else:
                    product["price"] = pricing_result.get("message", {}).get("products", {}).get(
                        list(pricing_result['message']['products'].keys())[0], {}).get("customer_type", {}).get(
                        "B2B", {}).get("storages", {}).get("1", {}).get("regular", 0)

                    special_price = pricing_result.get("message", {}).get("products", {}).get(
                        list(pricing_result['message']['products'].keys())[0], {}).get("customer_type", {}).get(
                        "B2B", {}).get("storages", {}).get("1", {})

                    now_formated_date_time = jdatetime.datetime.strptime(
                        jdatetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")

                    special_price_stored_date = special_price.get("special_to_date") if special_price.get(
                        "special_to_date") else jdatetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    special_formated_date_time = jdatetime.datetime.strptime(special_price_stored_date,
                                                                             "%Y-%m-%d %H:%M:%S")

                    if special_price.get("special") and now_formated_date_time < special_formated_date_time:
                        product["special_price"] = pricing_result.get("message", {}).get("products", {}).get(
                            list(pricing_result['message']['products'].keys())[0], {}).get("customer_type", {}).get(
                            "B2B", {}).get("storages", {}).get("1", {}).get("special", 0)

                    product_list.append(product)

            final_result['products'] = product_list
            if not product_list:
                raise HTTPException(status_code=404, detail={"error": "No products found"})
            return convert_case(final_result, 'camel')


@router.get("/get_product_list_by_system_code/{systemCode}/", tags=["Product"])
def get_product_list_by_system_code(
        response: Response,
        system_code: str = Path(..., alias='systemCode'),
        page: int = Query(1, alias='page'),
        per_page: int = Query(10, alias='perPage'),
        access: Optional[str] = Header(None),
        refresh: Optional[str] = Header(None)
):
    """
    Get product list by brand
    """
    customer_type = None
    allowed_storages = list()
    if access or refresh:
        user_data, tokens = auth_handler.check_current_user_tokens(access, refresh)
        customer_type = user_data.get("customer_type", ["B2B"])[0]
        allowed_storages = user_data.get("allowed_storages", [])

    quantity_available_result = test_rpc.publish(
        message={
            "quantity": {
                "action": "get_available_quantities",
                "body": {
                    "system_code": system_code,
                    "customer_type": customer_type if customer_type else "B2B",
                    "storages": allowed_storages if allowed_storages else ["1"]
                }
            }
        },
        headers={'quantity': True}
    ).get("quantity", {})
    product_result = test_rpc.publish(
        message={
            "product": {
                "action": "get_product_list_by_system_code",
                "body": {
                    "system_code": system_code,
                    "page": page,
                    "per_page": per_page,
                    "available_quantities": quantity_available_result.get("message", {})
                }
            }
        },
        headers={'product': True}
    )
    product_result = product_result.get("product", {})
    if product_result.get("success"):
        message_product = product_result.get("message", {})
        products_list = list()
        for product in message_product['products']:
            pricing_result = test_rpc.publish(
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
                if customer_type and allowed_storages:
                    price_tuples = list()
                    for system_code, prices in pricing_result.get("message", {}).get("products", {}).items():
                        customer_type_price = prices.get("customer_type", {}).get(customer_type, {})
                        for storage, storage_prices in customer_type_price.get("storages", {}).items():
                            if str(storage) in allowed_storages:
                                price_tuples.append((storage_prices.get("regular"), storage_prices.get("special")))

                    if not price_tuples:
                        continue

                    price_tuples.sort(key=lambda x: x[0])
                    price, special_price = price_tuples[0]
                    product["price"] = price
                    product["special_price"] = special_price
                else:
                    product["price"] = pricing_result.get("message", {}).get("products", {}).get(
                        list(pricing_result['message']['products'].keys())[0], {}).get("customer_type", {}).get(
                        "B2B", {}).get("storages", {}).get("1", {}).get("regular", None)
                    product["special_price"] = pricing_result.get("message", {}).get("products", {}).get(
                        list(pricing_result['message']['products'].keys())[0], {}).get("customer_type", {}).get(
                        "B2B", {}).get("storages", {}).get("1", {}).get("special", None)
                    if not product["price"]:
                        continue
            else:
                continue

            products_list.append(product)

        if not products_list:
            raise HTTPException(status_code=404, detail={"error": "products not found"})
        message_product['products'] = products_list
        response.status_code = product_result.get("status_code", 200)
        return convert_case(message_product, 'camel')
    raise HTTPException(status_code=product_result.get("status_code", 500),
                        detail={"error": product_result.get("error", "Something went wrong")})


@router.get("/get_category_list", tags=["Product"])
def get_category_list(
        response: Response,
        access: Optional[str] = Header(None),
        refresh: Optional[str] = Header(None)
):
    """
    Get category list
    """
    customer_type = None
    allowed_storages = None
    if access or refresh:
        user_data, tokens = auth_handler.check_current_user_tokens(access, refresh)
        customer_type = user_data.get("customer_type", ["B2B"])[0]
        allowed_storages = user_data.get("allowed_storages", [])

    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)

        quantity_available_result = rpc.publish(
            message={
                "quantity": {
                    "action": "get_available_quantities",
                    "body": {
                        "system_code": "1",
                        "customer_type": customer_type if customer_type else "B2B",
                        "storages": allowed_storages if allowed_storages else ["1"]
                    }
                }
            },
            headers={'quantity': True}
        ).get("quantity", {})

        product_result = rpc.publish(
            message={
                "product": {
                    "action": "get_category_list",
                    "body": {
                        "available_quantities": quantity_available_result.get("message", {})
                    }
                }
            },
            headers={'product': True}
        )
        product_result = product_result.get("product", {})
        if product_result.get("success"):
            message_product = product_result.get("message", {})
            product_list = list()
            for product in message_product['product']['items']:
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
                    if customer_type and allowed_storages:
                        price_tuples = list()
                        for system_code, prices in pricing_result.get("message", {}).get("products", {}).items():
                            customer_type_price = prices.get("customer_type", {}).get(customer_type, {})
                            for storage, storage_prices in customer_type_price.get("storages", {}).items():
                                if str(storage) in allowed_storages:
                                    price_tuples.append((storage_prices.get("regular"), storage_prices.get("special")))

                        if not price_tuples:
                            continue
                        price_tuples.sort(key=lambda x: x[0])
                        price, special_price = price_tuples[0]
                        product["price"] = price
                        product["special_price"] = special_price
                    else:
                        product["price"] = pricing_result.get("message", {}).get("products", {}).get(
                            list(pricing_result['message']['products'].keys())[0], {}).get("customer_type", {}).get(
                            "B2B", {}).get("storages", {}).get("1", {}).get("regular", None)
                        product["special_price"] = pricing_result.get("message", {}).get("products", {}).get(
                            list(pricing_result['message']['products'].keys())[0], {}).get("customer_type", {}).get(
                            "B2B", {}).get("storages", {}).get("1", {}).get("special", None)
                        if not product["price"]:
                            continue
                    product_list.append(product)
            if not product_list:
                raise HTTPException(status_code=404, detail={"error": "products not found"})
            message_product['product']['items'] = product_list
            response.status_code = product_result.get("status_code", 200)
            return convert_case(message_product, 'camel')
        raise HTTPException(status_code=product_result.get("status_code", 500),
                            detail={"error": product_result.get("error", "Something went wrong")})


@router.get("/get_product_list_back_office", tags=["Product"])
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
        lang: Optional[str] = Query("fa_ir")
):
    """
    Get product list in  back office
    """
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)

        system_codes_list = []

        quantity_result_filter = rpc.publish(
            message={
                "quantity": {
                    "action": "quantity_filter",
                    "body": {
                        "quantity_range": [quantity_from, quantity_to] if quantity_from or quantity_to else None,
                        "warehouses": warehouses,
                    }
                }
            },
            headers={'quantity': True}
        )

        if (quantity_from or quantity_to) and not quantity_result_filter.get("quantity", {}).get("message", {}).get(
                'system_codes', None):
            raise HTTPException(status_code=404, detail={"error": "No products found"})

        if quantity_from or quantity_to:
            system_codes_list = quantity_result_filter.get("quantity", {}).get("message", {}).get('system_codes', [])

        if price_from or price_to:
            system_codes = []
            if quantity_result_filter.get("quantity", {}).get("message", {}).get('system_codes', None):
                system_codes = quantity_result_filter.get("quantity", {}).get("message", {}).get('system_codes', [])
            price_result = rpc.publish(
                message={
                    "pricing": {
                        "action": "pricing_filter",
                        "body": {
                            "pricing_range": [price_from, price_to] if price_from or price_to else None,
                            "system_codes": system_codes
                        }
                    }
                },
                headers={'pricing': True}
            )
            if not price_result.get("pricing", {}).get("success", {}):
                raise HTTPException(status_code=404, detail={"error": "No products found"})

            system_codes_list = price_result.get("pricing", {}).get("message", {})

        product_result = rpc.publish(
            message={
                "product": {
                    "action": "get_product_list_back_office",
                    "body": {
                        "brands": brands,
                        "sellers": sellers,
                        "colors": colors,
                        "date": [date_from, date_to] if date_from or date_to else None,
                        "guarantees": guarantees,
                        "steps": steps,
                        "visible_in_site": visible_in_site,
                        "approved": approved,
                        "available": available,
                        "page": page,
                        "per_page": per_page,
                        "system_codes_list": system_codes_list,
                        "lang": lang
                    }
                }
            },
            headers={'product': True}
        )
        product_result = product_result.get("product", {})
        message_product = product_result.get("message", {})
        product_list = list()
        for product in message_product['products']:
            rpc.response_len_setter(response_len=2)
            rpc_result = rpc.publish(
                message={
                    "pricing": {
                        "action": "get_price",
                        "body": {
                            "system_code": product.get("system_code")
                        }
                    },
                    "quantity": {
                        "action": "get_quantity",
                        "body": {
                            "system_code": product.get("system_code")
                        }
                    }
                },
                headers={'pricing': True, "quantity": True}
            )

            pricing_result = rpc_result.get("pricing", {})
            quantity_result = rpc_result.get("quantity", {})
            # price_tuples = list()
            if product.get('products'):
                for config in product['products']:
                    if pricing_result.get("success"):
                        system_code = config.get("system_code")
                        rpc.response_len_setter(response_len=1)
                        get_stock_result = rpc.publish(
                            message={
                                "quantity": {
                                    "action": "get_stock",
                                    "body": {
                                        "system_code": system_code
                                    }
                                }
                            },
                            headers={'quantity': True}
                        )
                        get_stock_result = get_stock_result.get("quantity", {}).get("message", {})
                        for customer_type, customer_type_obj in pricing_result.get("message", {}).get(
                                "products", {}).get(system_code, {}).get("customer_type", {}).items():
                            for storage, storage_obj in customer_type_obj.get("storages", {}).items():
                                pricing_result['message']["products"][system_code]["customer_type"][customer_type][
                                    'storages'][storage]['warehouse_label'] = quantity_result.get("message", {}).get(
                                    "products",
                                    {}).get(
                                    system_code, {}).get("customer_types", {}).get(customer_type, {}).get("storages",
                                                                                                          {}).get(
                                    storage, {}).get("warehouse_label", None)

                                stock_msm = [stock.get("stock") for stock in
                                             get_stock_result.get("storages", []) if
                                             stock.get("storage_id") == storage]

                                quantity_result['message']["products"][system_code]["customer_types"][customer_type][
                                    'storages'][storage]['stock'] = stock_msm[0] if stock_msm else 0

                        config['price'] = pricing_result.get("message", {}).get("products", {}).get(system_code,
                                                                                                    {})
                    if quantity_result.get("success"):
                        system_code = config.get("system_code")
                        config['quantity'] = quantity_result.get("message", {}).get("products", {}).get(system_code,
                                                                                                        {})

            product_system_code = product.get("system_code")
            product['system_code'] = product_system_code[:9] + "-" + product_system_code[9:]
            product_list.append(product)
        message_product['products'] = product_list
        message_product['filters'][3]['options'] = quantity_result_filter.get("quantity", {}).get("message", {}).get(
            'storages', [])
        if product_result.get("success"):
            response.status_code = product_result.get("status_code", 200)
            return convert_case(message_product, 'camel')
        raise HTTPException(status_code=product_result.get("status_code", 500),
                            detail={"error": product_result.get("error", "Something went wrong")})
