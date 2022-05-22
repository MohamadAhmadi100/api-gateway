from fastapi import HTTPException
from source.routers.cart.app import add_and_edit_product
from source.message_broker.rabbit_server import RabbitRPC


class EditQuantity:
    def __init__(self, parent_system_code, system_code, storage_id, count):
        self.parent_system_code = parent_system_code
        self.system_code = system_code
        self.storage_id = storage_id
        self.count = count


def check_price_qty(auth_header, cart, response):
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        cart_result = cart
        # find product in cart and build product object
        products = []
        for cart_items in cart_result.get('products'):
            products.append({
                "systemCode": cart_items['systemCode'],
                "storage_id": cart_items['storageId'],
                "price": cart_items['price'],
                "count": cart_items['count'],
                "customer_type": auth_header[0].get('customer_type')[0],
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
        response_result = []
        for checkout_data in quantity_result['quantity']['message'][0]:
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
            final_result["user_info"] = {"user_id": auth_header[0].get("user_id")}
            for product in parent_system_code_result.get("products", []):
                if product.get("system_code") == checkout_data['systemCode']:
                    final_result["product"] = product
                    break
            # edit cart after checking
            # TODO response error handeling
            if checkout_data['quantity_checkout'] == "pass":  # and checkout_data['price_checkout'] == "pass"
                pass
            elif checkout_data['quantity_checkout'] == "edited":  # and checkout_data['price_checkout'] == "pass"
                object_to_edit = EditQuantity(checkout_data['parent_system_code'], checkout_data['systemCode'],
                                              checkout_data['storage_id'],
                                              checkout_data['new_quantity'] - checkout_data['count'])

                add_and_edit_product(item=object_to_edit, response=response, auth_header=auth_header)
                pass
                # cart_result = rpc.publish(
                #     message={
                #         "cart": {
                #             "action": "add_and_edit_product_in_cart",
                #             "body": {
                #                 "user_info": final_result.get("user_info"),
                #                 "product": final_result.get('product'),
                #                 "count": checkout_data.get("new_quantity"),
                #                 "storage_id": checkout_data.get("storage_id")
                #             }
                #         }
                #     },
                #     headers={'cart': True}
                # )
                # response_result.append(f'{item_name} quantity edited')

            elif checkout_data[
                'quantity_checkout'] == "system code not found":  # or checkout_data['price_checkout'] == "system code not found"
                pass
                # cart_result = rpc.publish(
                #     message={
                #         "cart": {
                #             "action": "remove_product_from_cart",
                #             "body": {
                #                 "user_id": user.get("user_id"),
                #                 "system_code": checkout_data["systemCode"],
                #                 "storage_id": checkout_data["storage_id"]
                #             }
                #         }
                #     },
                #     headers={'cart': True})
                # response_result.append(f'{item_name} not found and removed')
        if not response_result:
            return {"success": True, "message": "checkout completed"}
        else:
            return {"success": False, "message": response_result}
