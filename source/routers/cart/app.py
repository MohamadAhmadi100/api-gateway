from fastapi import FastAPI, HTTPException, Response, responses, Path, Depends
from starlette.exceptions import HTTPException as starletteHTTPException

from source.config import settings
from source.helpers.case_converter import convert_case
from source.message_broker.rabbit_server import RabbitRPC
from source.routers.cart.validators.cart import AddCart
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
    # check if all will have response(timeout)
    rpc.response_len_setter(response_len=3)
    result = rpc.publish(
        message={
            "product": {
                "action": "get_product_by_system_code",
                "body": {
                    "system_code": item.parent_system_code,
                    "lang": "fa_ir"
                }
            }, "pricing": {
                "action": "get_price",
                "body": {
                    "system_code": item.parent_system_code
                }
            }, "quantity": {
                "action": "get_quantity",
                "body": {
                    "system_code": item.parent_system_code
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
        product_result = product_result.get("message").copy()
        final_result = dict()
        final_result["user_info"] = {"user_id": user.get("user_id")}
        for product in product_result.get("products", []):
            if product.get("system_code") == item.system_code:
                product['name'] = product_result.get("name")
                final_result["product"] = product
                break

        # price actions

        main_price = pricing_result.get("message", {}).get("products", {}).get(item.system_code, {})
        customer_type_price = main_price.get("customer_type", {}).get(customer_type, {})
        storage_price = customer_type_price.get("storages", {}).get(item.storage_id, {})

        price = storage_price if storage_price else customer_type_price if customer_type_price else main_price

        final_result["price"] = price.get("special") if price.get("special") else price.get("regular")

        # quantity actions

        main_quantity = quantity_result.get("message", {}).get("products", {}).get(item.system_code, {})
        cusomer_type_quantity = main_quantity.get("customer_types", {}).get(customer_type, {})
        storage_quantity = cusomer_type_quantity.get("storages", {}).get(item.storage_id, {})

        quantity = storage_quantity if storage_quantity else cusomer_type_quantity if cusomer_type_quantity else main_quantity

        if quantity.get("stock_for_sale", 0) >= item.count:
            final_result["count"] = item.count
            final_result["storage_id"] = item.storage_id
        else:
            raise HTTPException(status_code=400,
                                detail={"error": "Not enough quantity"})

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
            return {"message": cart_result.get("message")}


@app.get("/cart/", tags=["Cart"])
def get_cart(response: Response, auth_header=Depends(auth_handler.check_current_user_tokens)) -> dict:
    """
    get user cart
    """
    user, token_dict = auth_header
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
        response.status_code = cart_result.get("status_code", 200)
        return convert_case(cart_result.get("message"), 'camel')


@app.delete("/cart/{systemCode}/{storageId}", status_code=200, tags=["Cart"])
def remove_product_from_cart(response: Response, auth_header=Depends(auth_handler.check_current_user_tokens),
                             storage_id: str = Path(..., min_length=1, max_length=2, alias='storageId'),
                             system_code: str = Path(..., min_length=12, max_length=12, alias='systemCode')) -> dict:
    """
    remove an item from cart
    """
    user, token_dict = auth_header
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
        return {"message": cart_result.get("message")}


@app.put("/checkout/", tags=["Cart"])
def checkout(response: Response, auth_header=Depends(auth_handler.check_current_user_tokens)) -> dict:
    # get user cart
    user, token_dict = auth_header
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
                    headers={'cart': True})
                response_result.append(f'{item_name} not found and removed')
        if not response_result:
            return {"success": True, "message": "checkout completed"}
        else:
            return {"success": True, "message": response_result}