import time

import jdatetime
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

                now_formated_date_time = jdatetime.datetime.strptime(
                    jdatetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")

                special_formated_date_time = jdatetime.datetime.strptime(price.get("special_to_date"),
                                                                         "%Y-%m-%d %H:%M:%S")

                if not price.get("special"):
                    product["price"] = price.get("regular")
                else:
                    if now_formated_date_time < special_formated_date_time and price.get(
                            "special"):
                        product["price"] = price.get("special")
                    else:
                        product["price"] = price.get("regular")

                product["quantity"] = quantity_result.get("message", {}).get("products", {}).get(
                    product.get("system_code"), {}).get("customer_types", {}).get(customer_type, {}).get("storages",
                                                                                                         {}).get(
                    product.get("storage_id"), {})

                if product.get("price"):
                    base_price += product.get("price") * product.get("count")

            cart_result["message"]["base_price"] = base_price

            total_price = base_price
            if cart_result["message"].get("shipment"):
                for storage_id, shipment in cart_result["message"]["shipment"].items():
                    total_price += shipment.get("customerPrice", 0)

            if cart_result["message"].get("payment") and cart_result["message"].get("payment").get("walletAmount"):
                total_price -= cart_result["message"]["payment"]['walletAmount']

            cart_result["message"]["total_price"] = total_price

            return cart_result
