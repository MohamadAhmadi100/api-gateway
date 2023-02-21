from datetime import datetime, timedelta
from typing import Optional

import jdatetime
from fastapi import FastAPI, HTTPException, Response, responses, Path, Depends, Query
from starlette.exceptions import HTTPException as starletteHTTPException
from starlette_prometheus import metrics, PrometheusMiddleware
from source.config import settings
from source.helpers.case_converter import convert_case
from source.message_broker.rabbit_server import RabbitRPC
from source.routers.cart.validators.cart import AddCart, AddCreditCart
from source.routers.customer.module.auth import AuthHandler

TAGS = [
    {
        "name": "Cart",
        "description": "Cart CRUD"
    }
]

app = FastAPI(
    title="Cart API",
    description="This is Cart gateway MicroService",
    version="0.1.0",
    openapi_tags=TAGS,
    docs_url="/docs/" if settings.DEBUG_MODE else None,
    redoc_url="/redoc/" if settings.DEBUG_MODE else None,
    debug=settings.DEBUG_MODE
)


# customize exception handler of fast api
@app.exception_handler(starletteHTTPException)
def validation_exception_handler(request, exc):
    return responses.JSONResponse(exc.detail, status_code=exc.status_code)


auth_handler = AuthHandler()


@app.put("/cart/", tags=["Cart"])
def add_and_edit_product(item: AddCart, response: Response, auth_header=Depends(auth_handler.check_current_user_tokens)
                         ) -> dict:
    """
    add and edit item in cart
    edit is based on product count and warehouse id
    """
    # get user from token
    user, token_dict = auth_header
    customer_type = user.get("customer_type")[0]
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=3)
        result = rpc.publish(
            message={
                "product": {
                    "action": "get_product_by_system_code",
                    "body": {
                        "system_code": item.system_code,
                        "lang": "fa_ir"
                    }
                },
                "customer": {
                    "action": "check_is_registered",
                    "body": {
                        "customer_phone_number": user.get("phone_number"),
                    }
                },
                "order": {
                    "action": "customer_products_report",
                    "body": {
                        "customer_id": user.get("user_id")
                    }
                }
            },
            headers={'product': True, "customer": True, "order": True},
        )
        product_result = result.get("product", {})
        customer_result = result.get("customer", {})
        order_result = result.get("order", {})
        if not product_result.get("success"):
            raise HTTPException(status_code=product_result.get("status_code", 500),
                                detail={"error": product_result.get("error", "Something went wrong")})
        elif not customer_result.get("message", {}).get('customerIsActive'):
            raise HTTPException(status_code=403, detail={"error": customer_result.get("message", {}).get('message')})
        else:

            ordered_count = [i.get("count") for i in order_result.get('customer_detail') if
                             i.get('system_code') == item.system_code and i.get("storage_id") == item.storage_id]
            ordered_count = ordered_count[0] if ordered_count else 0

            product_result = product_result.get("message").copy()
            final_result = dict()
            final_result["user_info"] = {"user_id": user.get("user_id")}
            cart_product = product_result.copy()
            del cart_product['visible_in_site']
            del cart_product['step']
            del cart_product['warehouse_details']
            final_result["product"] = cart_product

            # quantity actions

            quantity = product_result.get('warehouse_details', {}).get(customer_type, {}).get("storages", {}).get(
                item.storage_id, {})

            rpc.response_len_setter(response_len=1)
            user_cart = rpc.publish(
                message={
                    "cart": {
                        "action": "get_cart",
                        "body": {
                            "user_id": user.get("user_id")
                        }
                    }
                },
                headers={'cart': True}
            ).get('cart', {}).get('message', {})
            now_count = 0
            for cart_product in user_cart.get("products", []):
                if cart_product.get("system_code") == item.system_code and cart_product.get(
                        'storage_id') == item.storage_id:
                    now_count = cart_product.get("count", 0)
                    break
            for cart_credit in user_cart.get("credits", []):
                if cart_credit.get("system_code") == item.system_code and cart_credit.get(
                        'storage_id') == item.storage_id:
                    now_count += cart_credit.get("count", 0)
                    break

            allowed_count = (quantity.get("quantity", 0) - quantity.get('reserved', 0))
            if allowed_count >= (now_count + item.count):
                final_result["count"] = item.count
                final_result["storage_id"] = item.storage_id
            else:
                raise HTTPException(status_code=400,
                                    detail={"error": "موجودی این محصول کافی نیست"})

            if (now_count + item.count) < quantity.get('min_qty') or (
                    now_count + item.count + ordered_count) > quantity.get('max_qty'):
                response.status_code = 400
                raise HTTPException(status_code=400,
                                    detail={"error": "مقدار وارد شده بیش از حد مجاز است"})

            rpc.response_len_setter(response_len=1)
            cart_result = rpc.publish(
                message={
                    "cart": {
                        "action": "add_and_edit_product_in_cart",
                        "body": final_result
                    }
                },
                headers={'cart': True}
            )
            cart_result = cart_result.get("cart", {})
            if not cart_result.get("success"):
                raise HTTPException(status_code=product_result.get("status_code", 500),
                                    detail={"error": product_result.get("error", "Something went wrong")})
            else:
                response.status_code = cart_result.get("status_code", 200)
                return {"message": convert_case(cart_result.get("message"), "camel")}


@app.put("/credit_cart/", tags=["Cart"])
def add_and_edit_credit_product(
        item: AddCreditCart,
        response: Response,
        auth_header=Depends(auth_handler.check_current_user_tokens)
) -> dict:
    """
    add and edit credit items in cart
    edit is based on product count and warehouse id
    """
    # get user from token
    user, token_dict = auth_header
    customer_type = user.get("customer_type")[0]
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=4)
        result = rpc.publish(
            message={
                "product": {
                    "action": "get_product_by_system_code",
                    "body": {
                        "system_code": item.system_code,
                        "lang": "fa_ir"
                    }
                },
                "customer": {
                    "action": "check_is_registered",
                    "body": {
                        "customer_phone_number": user.get("phone_number"),
                    }
                },
                "order": {
                    "action": "customer_products_report",
                    "body": {
                        "customer_id": user.get("user_id")
                    }
                },
                "credit": {
                    "action": "get_credit_and_expire_date",
                    "body": {
                        "customer_id": str(user.get("user_id"))
                    }
                }
            },
            headers={'product': True, "customer": True, "order": True, "credit": True},
        )
        credit_result = result.get("credit", {})
        product_result = result.get("product", {})
        customer_result = result.get("customer", {})
        order_result = result.get("order", {})
        if not product_result.get("success") and customer_result.get("success") and credit_result.get("success"):
            raise HTTPException(status_code=product_result.get("status_code", 500),
                                detail={"error": product_result.get("error", "Something went wrong")})
        elif not customer_result.get("message", {}).get('customerIsActive'):
            raise HTTPException(status_code=403, detail={"error": customer_result.get("message", {}).get('message')})
        else:
            credit = credit_result.get("message")
            if jdatetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") > credit.get(
                    "expireDate"):
                raise HTTPException(status_code=403, detail={"error": "بازه ی خرید اعتباری شما به پایان رسیده است"})
            ordered_count = [i.get("count") for i in order_result.get('customer_detail') if
                             i.get('system_code') == item.system_code and i.get("storage_id") == item.storage_id]
            ordered_count = ordered_count[0] if ordered_count else 0

            product_result = product_result.get("message").copy()
            final_result = dict()
            final_result["days"] = item.days
            final_result["user_info"] = {"user_id": user.get("user_id")}
            cart_product = product_result.copy()
            del cart_product['visible_in_site']
            del cart_product['step']
            del cart_product['warehouse_details']
            final_result["product"] = cart_product

            # quantity actions

            quantity = product_result.get('warehouse_details', {}).get(customer_type, {}).get("storages", {}).get(
                item.storage_id, {})

            rpc.response_len_setter(response_len=1)
            user_cart = rpc.publish(
                message={
                    "cart": {
                        "action": "get_cart",
                        "body": {
                            "user_id": user.get("user_id")
                        }
                    }
                },
                headers={'cart': True}
            ).get('cart', {}).get('message', {})
            now_count = 0
            for cart_product in user_cart.get("products", []):
                if cart_product.get("system_code") == item.system_code and cart_product.get(
                        'storage_id') == item.storage_id:
                    now_count += cart_product.get("count", 0)
                    break
            for cart_credit in user_cart.get("credits", []):
                if cart_credit.get("system_code") == item.system_code and cart_credit.get(
                        'storage_id') == item.storage_id:
                    now_count += cart_credit.get("count", 0)
                    break

            cart_credit_price = rpc.publish(
                message={
                    "product": {
                        "action": "get_products_credit_price_by_system_codes",
                        "body": {
                            "product_list": user_cart.get("credits", []),
                            "lang": "fa_ir",
                            "customer_type": customer_type
                        }
                    }},
                headers={'product': True}
            ).get('product', {}).get('message', 0)

            product_storage = product_result.get("warehouse_details", {}).get(customer_type, {}).get(
                "storages", {}).get(item.storage_id)
            product_price = product_storage.get("regular", 0)
            product_credit = product_storage.get("credit")
            product_credit_days = product_credit.get("days", 0)
            expire_plus_now = (jdatetime.datetime.now() + jdatetime.timedelta(days=product_credit_days))
            if credit.get("expireDate") < expire_plus_now.strftime("%Y-%m-%d %H:%M:%S"):
                if product_credit.get("type") == "fixed":
                    raise HTTPException(
                        status_code=403,
                        detail={
                            "error":
                                "اجازه ی انتخاب کالای اعتبار ثابت با زمان بیشتر از اعتبار خود را ندارید"}
                    )
                elif product_credit.get("type") == "daily":
                    if credit.get("expireDate") - datetime.now().strftime("%Y-%m-%d %H:%M:%S") >= item.days:
                        raise HTTPException(
                            status_code=403,
                            detail={
                                "error":
                                    "اعتبار شما برای مدت زمان انتخابی کافی نیست"}
                        )

            if product_credit.get("type") == "fixed":
                credit_price = product_price + (
                        product_credit.get("percent", 0) * product_price
                ) + product_credit.get("regular", 0)
            elif product_credit.get("type") == "daily":
                credit_price = product_price + (
                        (product_credit.get("percent", 0) * product_price) + product_credit.get("regular", 0)
                ) * item.days
            if credit.get("creditAmount") - cart_credit_price < credit_price:
                raise HTTPException(status_code=403,
                                    detail={"error": "قیمت کالا ی انتخابی بیشتر از سقف قیمت اعتبار است"})
            allowed_count = (quantity.get("quantity", 0) - quantity.get('reserved', 0))
            if allowed_count >= (now_count + item.count):
                final_result["count"] = item.count
                final_result["storage_id"] = item.storage_id
            else:
                raise HTTPException(status_code=400,
                                    detail={"error": "موجودی این محصول کافی نیست"})

            if (now_count + item.count) < quantity.get('min_qty') or (
                    now_count + item.count + ordered_count) > quantity.get('max_qty'):
                response.status_code = 400
                raise HTTPException(status_code=400,
                                    detail={"error": "مقدار وارد شده بیش از حد مجاز است"})

            rpc.response_len_setter(response_len=1)
            cart_result = rpc.publish(
                message={
                    "cart": {
                        "action": "add_and_edit_credit_in_cart",
                        "body": final_result
                    }
                },
                headers={'cart': True}
            )
            cart_result = cart_result.get("cart", {})
            if not cart_result.get("success"):
                raise HTTPException(status_code=product_result.get("status_code", 500),
                                    detail={"error": product_result.get("error", "Something went wrong")})
            else:
                response.status_code = cart_result.get("status_code", 200)
                return {"message": convert_case(cart_result.get("message"), "camel")}


@app.get("/cart/", tags=["Cart"])
def get_cart(response: Response,
             informal: Optional[bool] = Query(False),
             auth_header=Depends(auth_handler.check_current_user_tokens)
             ) -> dict:
    """
    get user cart
    """
    user, token_dict = auth_header
    user_id = user.get("user_id")
    customer_type = user.get("customer_type")[0]
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        result = rpc.publish(
            message={
                "cart": {
                    "action": "get_cart",
                    "body": {
                        "user_id": user_id
                    }
                }
            },
            headers={'cart': True}
        )
        cart_result = result.get("cart", {})
        if not cart_result.get("success"):
            raise HTTPException(status_code=cart_result.get("status_code", 500),
                                detail={"error": cart_result.get("error", "Something went wrong")})
        else:
            base_price = 0
            profit = 0
            for product in cart_result["message"]["products"]:
                rpc.response_len_setter(response_len=1)
                product_result = rpc.publish(
                    message={
                        "product": {
                            "action": "get_product_backoffice",
                            "body": {
                                "system_code": product.get("system_code")
                            }
                        }
                    },
                    headers={'product': True}
                ).get("product", {}).get("message", {})
                storage_details = product_result.get("warehouse_details", {}).get(customer_type, {}).get("storages",
                                                                                                         {}).get(
                    product.get("storage_id"), {})

                now_formated_date_time = jdatetime.datetime.strptime(
                    jdatetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")

                if not storage_details.get("special"):
                    product["price"] = storage_details.get("regular")
                else:
                    special_formated_date_time = jdatetime.datetime.strptime(
                        storage_details.get("special_to_date", jdatetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                        "%Y-%m-%d %H:%M:%S")
                    if now_formated_date_time < special_formated_date_time and storage_details.get(
                            "special"):
                        product["price"] = storage_details.get("special")
                        profit += (storage_details.get("regular") - storage_details.get("special")) * product.get(
                            "count")
                    else:
                        product["price"] = storage_details.get("regular")

                if informal:
                    product["price"] = storage_details.get("informal") if storage_details.get("informal") else product[
                        "price"]

                avaible_count = (storage_details.get("quantity", 0) - storage_details.get("reserved", 0))

                product["quantity"] = {
                    "storageId": storage_details.get("storage_id"),
                    "minQty": storage_details.get("min_qty"),
                    "maxQty": storage_details.get("max_qty", 0) if avaible_count > storage_details.get(
                        "max_qty", 0) else avaible_count,
                    "warehouseState": storage_details.get("warehouse_state"),
                    "warehouseCity": storage_details.get("warehouse_city"),
                    "warehouseStateId": storage_details.get("warehouse_state_id"),
                    "warehouseCityId": storage_details.get("warehouse_city_id"),
                    "warehouseLabel": storage_details.get("warehouse_label"),
                }

                if product.get("price"):
                    base_price += product.get("price") * product.get("count")

            # ======================= Add Baskets to base price =================================== #

            baskets = cart_result.get("message").get("baskets")
            new_baskets = []
            if baskets and type(baskets) == dict:
                for key, basket in baskets.items():
                    basket_name = ""
                    if type(basket) == list:
                        for item in basket:
                            single_basket_price = 0
                            basket_product_count = 0
                            storage_id = 0
                            if type(item.get("mandatory_products")) == list and len(item.get("mandatory_products")):
                                basket_product_count += len(item.get("mandatory_products"))
                                for product in item.get("mandatory_products"):
                                    regular_price = product.get("regular") or False
                                    if regular_price and type(regular_price) == int and regular_price > product.get(
                                            "price"):
                                        profit += (regular_price - product.get("price")) * product.get("count")
                                    base_price += product.get("price") * product.get("count")
                                    single_basket_price += product.get("price") * product.get("count")
                                    storage_id = storage_id or product.get("storage_id")
                            if type(item.get("selective_products")) == list and len(item.get("selective_products")):
                                basket_product_count += len(item.get("selective_products"))
                                for product in item.get("selective_products"):
                                    regular_price = product.get("regular")
                                    if regular_price and type(regular_price) == int and regular_price > product.get(
                                            "price"):
                                        profit += (regular_price - product.get("price")) * product.get("count")
                                    base_price += product.get("price") * product.get("count")
                                    single_basket_price += product.get("price") * product.get("count")
                                    storage_id = storage_id or product.get("storage_id")
                            if type(item.get("optional_products")) == list and len(item.get("optional_products")):
                                basket_product_count += len(item.get("optional_products"))
                                for product in item.get("optional_products"):
                                    regular_price = product.get("regular")
                                    if regular_price and type(regular_price) == int and regular_price > product.get(
                                            "price"):
                                        profit += (regular_price - product.get("price")) * product.get("count")
                                    base_price += product.get("price") * product.get("count")
                                    single_basket_price += product.get("price") * product.get("count")
                                    storage_id = storage_id or product.get("storage_id")
                            item["basket_price"] = single_basket_price
                            item["basket_product_count"] = basket_product_count
                            if item.get("basket_name"):
                                basket_name = item.get("basket_name")
                        new_baskets.append({"basketId": key,
                                            "basketName": basket_name,
                                            "count": len(basket),
                                            "baskets": basket,
                                            "storageId": storage_id})
            cart_result["message"]["baskets"] = new_baskets
            cart_result["message"]["base_price"] = base_price

            # ======================= Add Coupon to base price =================================== #


            cart_credit_price = 0
            if cart_result.get("message").get("credits"):
                cart_credit_price = rpc.publish(
                    message={
                        "product": {
                            "action": "get_products_credit_price_by_system_codes",
                            "body": {
                                "product_list": cart_result.get("message").get("credits", []),
                                "lang": "fa_ir",
                                "customer_type": customer_type
                            }
                        }},
                    headers={'product': True}
                ).get('product', {}).get('message', 0)

            total_price = base_price
            if cart_result["message"].get("shipment"):
                for storage_id, shipment in cart_result["message"]["shipment"].items():
                    total_price += shipment.get("customerPrice", 0)

            grand_price = total_price
            coupon = cart_result.get("message").get("coupon")
            if coupon and type(coupon) == dict and coupon.get("discountValue"):
                # base_price -= coupon.get("discountValue")
                profit += coupon.get("discountValue")
                total_price -= coupon.get("discountValue")
            if cart_result["message"].get("payment") and cart_result["message"].get("payment").get("walletAmount"):
                total_price -= cart_result["message"]["payment"]['walletAmount']

            base_price += cart_credit_price
            cart_result['message']['grand_price'] = grand_price
            cart_result["message"]["total_price"] = int(total_price)
            cart_result['message']['profit'] = profit
            cart_result['message']['credit'] = cart_credit_price
            response.status_code = cart_result.get("status_code", 200)
            return convert_case(cart_result.get("message"), 'camel')


@app.delete("/cart/{systemCode}/{storageId}", status_code=200, tags=["Cart"])
def remove_product_from_cart(response: Response, auth_header=Depends(auth_handler.check_current_user_tokens),
                             storage_id: str = Path(..., min_length=1, max_length=2, alias='storageId'),
                             system_code: str = Path(..., min_length=25, max_length=25, alias='systemCode')) -> dict:
    """
    remove an item from cart
    """
    user, token_dict = auth_header
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        result = rpc.publish(
            message={
                "cart": {
                    "action": "remove_product_from_cart",
                    "body": {
                        "user_id": user.get("user_id"),
                        "system_code": system_code,
                        "storage_id": storage_id
                    }
                }
            },
            headers={'cart': True}
        )
        cart_result = result.get("cart", {})
        if not cart_result.get("success"):
            raise HTTPException(status_code=cart_result.get("status_code", 500),
                                detail={"error": cart_result.get("error", "Something went wrong")})
        else:
            response.status_code = cart_result.get("status_code", 200)
            return {"message": convert_case(cart_result.get("message"), "camel")}


@app.delete("/cart/basket/{basketId}", status_code=200, tags=["Cart"])
def basket_remove(
        response: Response,
        auth_header=Depends(auth_handler.check_current_user_tokens),
        basket_id: str = Path(..., alias='basketId')
) -> dict:
    """
    remove an item from cart
    """
    user, token_dict = auth_header
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        result = rpc.publish(
            message={
                "cart": {
                    "action": "basket_remove",
                    "body": {
                        "user_id": user.get("user_id"),
                        "basket_id": basket_id,
                    }
                }
            },
            headers={'cart': True}
        )
        cart_result = result.get("cart", {})
        if not cart_result.get("success"):
            raise HTTPException(status_code=cart_result.get("status_code", 500),
                                detail={"error": cart_result.get("error", "Something went wrong")})
        else:
            response.status_code = cart_result.get("status_code", 200)
            return {"message": convert_case(cart_result.get("message"), "camel")}


@app.delete("/cart/coupon", status_code=200, tags=["Cart"])
def remove_coupon(
        response: Response,
        auth_header=Depends(auth_handler.check_current_user_tokens),
) -> dict:
    """
    remove an item from cart
    """
    user, token_dict = auth_header
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        result = rpc.publish(
            message={
                "cart": {
                    "action": "delete_coupon_from_cart",
                    "body": {
                        "user_id": user.get("user_id")
                    }
                }
            },
            headers={'cart': True}
        )
        cart_result = result.get("cart", {})
        if not cart_result.get("success"):
            raise HTTPException(status_code=cart_result.get("status_code", 500),
                                detail={"error": cart_result.get("error", "Something went wrong")})
        response.status_code = cart_result.get("status_code", 200)
        return {"message": cart_result.get("message")}


@app.put("/checkout/", tags=["Cart"])
def checkout(response: Response, auth_header=Depends(auth_handler.check_current_user_tokens)) -> dict:
    # get user cart
    user, token_dict = auth_header
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        result = rpc.publish(
            message={
                "cart": {
                    "action": "get_cart",
                    "body": {
                        "user_id": user.get("user_id")
                    }
                }
            },
            headers={'cart': True}
        )
        cart_result = result.get("cart", {})
        if not cart_result.get("success"):
            raise HTTPException(status_code=cart_result.get("status_code", 500),
                                detail={"error": cart_result.get("error", "Something went wrong")})
        else:

            # find product in cart and build product object
            products = []
            for cart_items in cart_result.get('message')['products']:
                products.append({
                    "systemCode": cart_items['system_code'],
                    "storage_id": cart_items['storage_id'],
                    "price": cart_items['price'],
                    "count": cart_items['count'],
                    "customer_type": user.get('customer_type')[0],
                    "name": cart_items.get('name')

                })
            # check quantity
            rpc.response_len_setter(response_len=1)
            quantity_result = rpc.publish(
                message={
                    "quantity": {
                        "action": "get_quantity_list",
                        "body": {
                            "item": products
                        }
                    }
                },
                headers={'quantity': True}
            )
            # check price
            rpc.response_len_setter(response_len=1)
            price_result = rpc.publish(
                message={
                    "pricing": {
                        "action": "get_price_list",
                        "body": {
                            "item": quantity_result['quantity']['message'][0]
                        }
                    }
                },
                headers={'pricing': True}
            )
            # actions in cart product objects afret checking
            response_result = []
            for checkout_data in price_result['pricing']['message'][0]:
                item_name = checkout_data.get('name')
                rpc.response_len_setter(response_len=1)
                # get product data
                parent_system_code_result = rpc.publish(
                    message={
                        "product": {
                            "action": "get_product_by_system_code",
                            "body": {
                                "system_code": checkout_data['parent_system_code'],
                                "lang": "fa_ir"
                            }
                        }
                    },
                    headers={'product': True}
                )
                parent_system_code_result = parent_system_code_result['product'].get("message").copy()
                final_result = dict()
                final_result["user_info"] = {"user_id": user.get("user_id")}
                for product in parent_system_code_result.get("products", []):
                    if product.get("system_code") == checkout_data['systemCode']:
                        final_result["product"] = product
                        break
                # edit cart after checking
                if checkout_data['quantity_checkout'] == "pass" and checkout_data['price_checkout'] == "pass":
                    pass
                elif checkout_data['quantity_checkout'] == "pass" and checkout_data['price_checkout'] == "edited":
                    cart_result = rpc.publish(
                        message={
                            "cart": {
                                "action": "add_and_edit_product_in_cart",
                                "body": {
                                    "user_info": final_result.get("user_info"),
                                    "product": final_result.get('product'),
                                    "price": checkout_data.get("new_price"),
                                    "count": checkout_data.get("count"),
                                    "storage_id": checkout_data.get("storage_id")
                                }
                            }
                        },
                        headers={'cart': True}
                    )

                    response_result.append(f'{item_name} price edited')
                elif checkout_data['quantity_checkout'] == "edited" and checkout_data['price_checkout'] == "pass":
                    cart_result = rpc.publish(
                        message={
                            "cart": {
                                "action": "add_and_edit_product_in_cart",
                                "body": {
                                    "user_info": final_result.get("user_info"),
                                    "product": final_result.get('product'),
                                    "price": checkout_data.get("price"),
                                    "count": checkout_data.get("new_quantity"),
                                    "storage_id": checkout_data.get("storage_id")
                                }
                            }
                        },
                        headers={'cart': True}
                    )
                    response_result.append(f'{item_name} quantity edited')
                elif checkout_data['quantity_checkout'] == "edited" and checkout_data['price_checkout'] == "edited":
                    cart_result = rpc.publish(
                        message={
                            "cart": {
                                "action": "add_and_edit_product_in_cart",
                                "body": {
                                    "user_info": final_result.get("user_info"),
                                    "product": final_result.get('product'),
                                    "price": checkout_data.get("new_price"),
                                    "count": checkout_data.get("new_quantity"),
                                    "storage_id": checkout_data.get("storage_id")
                                }
                            }
                        },
                        headers={'cart': True}
                    )
                    response_result.append(f'{item_name} quantity and price edited')
                elif checkout_data['quantity_checkout'] == "system code not found" or checkout_data[
                    'price_checkout'] == "system code not found":
                    result = rpc.publish(
                        message={
                            "cart": {
                                "action": "remove_product_from_cart",
                                "body": {
                                    "user_id": user.get("user_id"),
                                    "system_code": checkout_data["systemCode"],
                                    "storage_id": checkout_data["storage_id"]
                                }
                            }
                        },
                        headers={'cart': True}
                    )
                    response_result.append(f'{item_name} not found and removed')
            if not response_result:
                return {"success": True, "message": "checkout completed"}
            else:
                return {"success": True, "message": response_result}
