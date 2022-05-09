from fastapi import HTTPException

from source.message_broker.rabbit_server import RabbitRPC


def get_cart(user):
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
            for product in cart_result["message"]["products"]:
                rpc.response_len_setter(response_len=2)
                pricing_result = rpc.publish(
                    message={
                        "pricing": {
                            "action": "get_price",
                            "body": {
                                "system_code": product.get("parent_system_code")
                            }
                        },
                        "quantity": {
                            "action": "get_quantity",
                            "body": {
                                "system_code": product.get("parent_system_code")
                            }
                        }
                    },
                    headers={'pricing': True, "quantity": True}
                )
                quantity_result = pricing_result.get("quantity", {})
                pricing_result = pricing_result.get("pricing", {})

                main_price = pricing_result.get("message", {}).get("products", {}).get(product.get("system_code"), {})
                customer_type_price = main_price.get("customer_type", {}).get(customer_type, {})
                storage_price = customer_type_price.get("storages", {}).get(product.get("storage_id"), {})

                price = storage_price if storage_price else customer_type_price if customer_type_price else main_price

                product["price"] = price.get("special") if price.get("special") else price.get("regular")

                product["quantity"] = quantity_result.get("message", {}).get("products", {}).get(
                    product.get("system_code"), {}).get("customer_types", {}).get(customer_type, {}).get("storages",
                                                                                                         {}).get(
                    product.get("storage_id"), {})

                base_price += product.get("price") * product.get("count")

            cart_result["message"]["base_price"] = base_price
            # need to add shipping price
            cart_result["message"]["total_price"] = base_price

            return cart_result
