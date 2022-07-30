from typing import Optional, List

from fastapi import HTTPException, APIRouter, Response, Path, Body, Query

from source.helpers.case_converter import convert_case
from source.helpers.create_class import CreateClass
from source.message_broker.rabbit_server import RabbitRPC
from source.routers.product.validators.price_models import UpdatePrice
from source.routers.product.validators.kowsar import KowsarConfig, KowsarGroup, KowsarPart
from source.routers.product.validators.price_models import Price
from source.routers.product.validators.product import Product, AddAttributes
from source.routers.product.validators.quantity_models import UpdateQuantity, Quantity

router = APIRouter()


@router.post("/kowsar/static/")
def create_kowsar_static_configs(item: KowsarConfig):
    """
    Create a new kowsar group
    """
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        product_result = rpc.publish(
            message={
                "product": {
                    "action": "create_kowsar_static_configs",
                    "body": {
                        "config_type": item.config_type,
                        "system_code": item.system_code,
                        "name": item.name,
                    }
                }
            },
            headers={'product': True}
        )
        product_result = product_result.get("product", {})
        if product_result.get("success"):
            return convert_case({"message": product_result.get("message")}, 'camel')
        raise HTTPException(status_code=product_result.get("status_code", 500),
                            detail={"error": product_result.get("error", "Something went wrong")})


# get kowsar static configs by config_type
@router.get("/kowsar/static/{config_type}/")
def get_kowsar_static_configs_by_config_type(config_type: str):
    """
    Get kowsar static configs by config_type
    """
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        product_result = rpc.publish(
            message={
                "product": {
                    "action": "get_kowsar_static_configs_by_config_type",
                    "body": {
                        "config_type": config_type,
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


@router.post("/kowsar/create_kowsar_group/")
def create_kowsar_group(
        response: Response,
        item: KowsarGroup
):
    """
    Create kowsar group
    """
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        product_result = rpc.publish(
            message={
                "product": {
                    "action": "create_kowsar_group",
                    "body": {
                        "system_code": item.system_code,
                        "name": item.name,
                        "parent_system_code": item.parent_system_code,
                        "configs": item.configs
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


@router.post("/kowsar/create_system_code/")
def create_system_code(
        response: Response,
        item: KowsarPart
):
    """
    Create kowsar system code
    """
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        product_result = rpc.publish(
            message={
                "product": {
                    "action": "create_system_code",
                    "body": {
                        "system_code": item.system_code,
                        "storage_ids": item.storage_ids,
                        "parent_system_code": item.parent_system_code,
                        "guaranty": item.guaranty
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


@router.get("/kowsar/items/{systemCode}/")
def get_kowsar_items(
        response: Response,
        system_code: str = Path(..., min_length=2, max_length=16, alias='systemCode')
):
    """
    Get children of kowsar item
    """
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
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


@router.post("/product/create_product/")
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


@router.get("/product/get_product_attributes/{systemCode}/")
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


@router.post("/product/add_attributes/")
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


@router.get("/product/get_backoffice/")
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


@router.post("/product/price/")
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


@router.put("/product/price/")
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
        pricing_result = pricing_result.get("product", {})
        if pricing_result.get("success"):
            response.status_code = pricing_result.get("status_code", 200)
            return {"message": pricing_result.get("message")}
        raise HTTPException(status_code=pricing_result.get("status_code", 500),
                            detail={"error": pricing_result.get("error", "Something went wrong")})


@router.get("/product/stock/{systemCode}/")
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


@router.post("/product/quantity/")
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


@router.put("/product/quantity/")
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


@router.get("/product/get_product_list_back_office/")
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

        # system_codes_list = []
        #
        # quantity_result_filter = rpc.publish(
        #     message={
        #         "quantity": {
        #             "action": "quantity_filter",
        #             "body": {
        #                 "quantity_range": [quantity_from, quantity_to] if quantity_from or quantity_to else None,
        #                 "warehouses": warehouses,
        #             }
        #         }
        #     },
        #     headers={'quantity': True}
        # )
        #
        # if (quantity_from or quantity_to) and not quantity_result_filter.get("quantity", {}).get("message", {}).get(
        #         'system_codes', None):
        #     raise HTTPException(status_code=404, detail={"error": "No products found"})
        #
        # if quantity_from or quantity_to:
        #     system_codes_list = quantity_result_filter.get("quantity", {}).get("message", {}).get('system_codes', [])
        #
        # if price_from or price_to:
        #     system_codes = []
        #     if quantity_result_filter.get("quantity", {}).get("message", {}).get('system_codes', None):
        #         system_codes = quantity_result_filter.get("quantity", {}).get("message", {}).get('system_codes', [])
        #     price_result = rpc.publish(
        #         message={
        #             "pricing": {
        #                 "action": "pricing_filter",
        #                 "body": {
        #                     "pricing_range": [price_from, price_to] if price_from or price_to else None,
        #                     "system_codes": system_codes
        #                 }
        #             }
        #         },
        #         headers={'pricing': True}
        #     )
        #     if not price_result.get("pricing", {}).get("success", {}):
        #         raise HTTPException(status_code=404, detail={"error": "No products found"})
        #
        #     system_codes_list = price_result.get("pricing", {}).get("message", {})

        product_result = rpc.publish(
            message={
                "product": {
                    "action": "get_product_list_back_office",
                    "body": {
                    }
                }
            },
            headers={'product': True}
        )
        product_result = product_result.get("product", {})
        message_product = product_result.get("message", {})

        # product_list = list()
        # for product in message_product['products']:
        #     rpc.response_len_setter(response_len=2)
        #     rpc_result = rpc.publish(
        #         message={
        #             "pricing": {
        #                 "action": "get_price",
        #                 "body": {
        #                     "system_code": product.get("system_code")
        #                 }
        #             },
        #             "quantity": {
        #                 "action": "get_quantity",
        #                 "body": {
        #                     "system_code": product.get("system_code")
        #                 }
        #             }
        #         },
        #         headers={'pricing': True, "quantity": True}
        #     )
        #
        #     pricing_result = rpc_result.get("pricing", {})
        #     quantity_result = rpc_result.get("quantity", {})
        #     # price_tuples = list()
        #     if product.get('products'):
        #         for config in product['products']:
        #             if pricing_result.get("success"):
        #                 system_code = config.get("system_code")
        #                 rpc.response_len_setter(response_len=1)
        #                 get_stock_result = rpc.publish(
        #                     message={
        #                         "quantity": {
        #                             "action": "get_stock",
        #                             "body": {
        #                                 "system_code": system_code
        #                             }
        #                         }
        #                     },
        #                     headers={'quantity': True}
        #                 )
        #                 get_stock_result = get_stock_result.get("quantity", {}).get("message", {})
        #                 for customer_type, customer_type_obj in pricing_result.get("message", {}).get(
        #                         "products", {}).get(system_code, {}).get("customer_type", {}).items():
        #                     for storage, storage_obj in customer_type_obj.get("storages", {}).items():
        #                         pricing_result['message']["products"][system_code]["customer_type"][customer_type][
        #                             'storages'][storage]['warehouse_label'] = quantity_result.get("message", {}).get(
        #                             "products",
        #                             {}).get(
        #                             system_code, {}).get("customer_types", {}).get(customer_type, {}).get("storages",
        #                                                                                                   {}).get(
        #                             storage, {}).get("warehouse_label", None)
        #
        #                         stock_msm = [stock.get("stock") for stock in
        #                                      get_stock_result.get("storages", []) if
        #                                      stock.get("storage_id") == storage]
        #
        #                         if quantity_result.get("success"):
        #                             quantity_result.setdefault("message", {}).setdefault('products', {}).setdefault(
        #                                 system_code, {}).setdefault("customer_types", {}).setdefault(customer_type,
        #                                                                                              {}).setdefault(
        #                                 'storages', {}).setdefault(storage, {})['stock'] = stock_msm[
        #                                 0] if stock_msm else 0
        #
        #                 config['price'] = pricing_result.get("message", {}).get("products", {}).get(system_code,
        #                                                                                             {})
        #             if quantity_result.get("success"):
        #                 system_code = config.get("system_code")
        #                 config['quantity'] = quantity_result.get("message", {}).get("products", {}).get(system_code,
        #                                                                                                 {})
        #
        #     product_system_code = product.get("system_code")
        #     product['system_code'] = product_system_code[:9] + "-" + product_system_code[9:]
        #     product_list.append(product)
        # message_product['products'] = product_list
        # message_product['filters'][3]['options'] = quantity_result_filter.get("quantity", {}).get("message", {}).get(
        #     'storages', [])
        if product_result.get("success"):
            response.status_code = product_result.get("status_code", 200)
            return convert_case(message_product, 'camel')
        raise HTTPException(status_code=product_result.get("status_code", 500),
                            detail={"error": product_result.get("error", "Something went wrong")})
