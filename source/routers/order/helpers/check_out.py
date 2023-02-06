from source.message_broker.rabbit_server import RabbitRPC
from source.routers.cart.app import add_and_edit_product
from source.routers.product.modules.allowed_storages import get_allowed_storages


class EditQuantity:
    def __init__(self, system_code, storage_id, count):
        self.system_code = system_code
        self.storage_id = storage_id
        self.count = count


def check_price_qty(auth_header, cart, response):
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        cart_result = cart
        # find product in cart and build product object
        allowed_storages = get_allowed_storages(auth_header[0].get("user_id"))
        products = []
        edited_result = []
        if cart_result.get('products'):
            for cart_items in cart_result.get('products'):
                if cart_items['storageId'] in allowed_storages:
                    if cart_items['price'] is None:
                        result = rpc.publish(
                            message={
                                "cart": {
                                    "action": "remove_product_from_cart",
                                    "body": {
                                        "user_id": auth_header[0].get("user_id"),
                                        "system_code": cart_items['systemCode'],
                                        "storage_id": cart_items['storageId']
                                    }
                                }
                            },
                            headers={'cart': True}
                        )
                        edited_result.append({
                            "name": cart_items['name'],
                            "status": "removed",
                            "message": f"{cart_items['name']} از سبد خرید به دلیل تغییر تایپ مشتری حذف شد"
                        })
                    else:
                        products.append({
                            "systemCode": cart_items['systemCode'],
                            "storage_id": cart_items['storageId'],
                            "price": cart_items['price'] if cart_items['price'] else 0,
                            "count": cart_items['count'],
                            "customer_type": auth_header[0].get('customer_type')[0],
                            "name": cart_items.get('name')

                        })
                else:
                    rpc.publish(
                        message={
                            "cart": {
                                "action": "remove_product_from_cart",
                                "body": {
                                    "user_id": auth_header[0].get("user_id"),
                                    "system_code": cart_items['systemCode'],
                                    "storage_id": cart_items['storageId']
                                }
                            }
                        },
                        headers={'cart': True}
                    )
                    edited_result.append({
                        "name": cart_items.get('name'),
                        "status": "removed",
                        "message": f"{cart_items.get('name')} از سبد خرید به دلیل عدم تطبیق ادرس با انبار انتخاب شده حذف شد"
                    })
            # check quantity
            if not products:
                return {"success": False, "message": edited_result}
            rpc.response_len_setter(response_len=1)
            quantity_result = rpc.publish(
                message={
                    "product": {
                        "action": "get_quantity_list",
                        "body": {
                            "item": products
                        }
                    }
                },
                headers={'product': True}
            )

            for checkout_data in quantity_result['product']['message'][0]:

                rpc.response_len_setter(response_len=1)
                # get product data
                if checkout_data['quantity_checkout'] == 'system code not found':
                    rpc.response_len_setter(response_len=1)
                    result = rpc.publish(
                        message={
                            "cart": {
                                "action": "remove_product_from_cart",
                                "body": {
                                    "user_id": auth_header[0].get("user_id"),
                                    "system_code": checkout_data['systemCode'],
                                    "storage_id": checkout_data['storage_id']
                                }
                            }
                        },
                        headers={'cart': True}
                    )
                    edited_result.append({
                        "name": checkout_data['name'],
                        "status": "removed",
                        "message": f"{checkout_data['name']} از سبد خرید به دلیل اتمام موجودی حذف شد"
                    })
                else:
                    # edit cart after checking
                    # TODO response error handeling
                    if checkout_data['quantity_checkout'] == "pass":  # and checkout_data['price_checkout'] == "pass"
                        pass
                    elif checkout_data[
                        'quantity_checkout'] == "edited":  # and checkout_data['price_checkout'] == "pass"
                        object_to_edit = EditQuantity(checkout_data['systemCode'], checkout_data['storage_id'],
                                                      checkout_data['new_quantity'] - checkout_data['count'])

                        edit = add_and_edit_product(item=object_to_edit, response=response, auth_header=auth_header)
                        if edit.get("error") is not None:
                            rpc.response_len_setter(response_len=1)
                            rpc.publish(
                                message={
                                    "cart": {
                                        "action": "remove_product_from_cart",
                                        "body": {
                                            "user_id": auth_header[0].get("user_id"),
                                            "system_code": checkout_data['systemCode'],
                                            "storage_id": checkout_data['storage_id']
                                        }
                                    }
                                },
                                headers={'cart': True}
                            )
                            edited_result.append({
                                "name": checkout_data['name'],
                                "status": "removed",
                                "message": f"{checkout_data['name']} از سبد خرید به دلیل اتمام موجودی حذف شد",

                            })
                        else:
                            edited_result.append({
                                "name": checkout_data['name'],
                                "status": "edited",
                                "message": f"{checkout_data['name']} از سبد خرید به دلیل اتمام موجودی حذف شد",
                            })
        if cart_result.get('baskets'):
            if cart_result.get('baskets'):
                rpc.response_len_setter(response_len=1)
                basket_checkout = rpc.publish(
                    message={
                        "basket": {
                            "action": "checkout_check_basket",
                            "body": {
                                "baskets": cart_result.get('baskets'),
                            }
                        }
                    },
                    headers={'basket': True}
                ).get("basket")
                if not basket_checkout['success']:
                    rpc.response_len_setter(response_len=1)
                    rpc.publish(
                        message={
                            "cart": {
                                "action": "delete_basket",
                                "body": {
                                    "user_id": auth_header[0].get("user_id"),
                                }
                            }
                        },
                        headers={'cart': True}
                    ).get("cart")
                    for cursor in cart['baskets']:
                        edited_result.append({
                            "name": cursor['basketName'],
                            "status": "deleted",
                            "message": f"{cursor['basketName']} از سبد خرید به دلیل مشکلات فنی حذف شد",
                        })
                elif basket_checkout['failed']:
                    rpc.response_len_setter(response_len=1)
                    rpc.publish(
                        message={
                            "cart": {
                                "action": "replace_basket_to_cart",
                                "body": {
                                    "user_id": auth_header[0].get("user_id"),
                                    "baskets": basket_checkout.get("result"),
                                }
                            }
                        },
                        headers={'cart': True}
                    ).get("cart")
                    edited_result = edited_result + basket_checkout.get("failed")
                else:
                    pass
        if not edited_result:
            return {"success": True, "message": "checkout completed"}
        else:
            return {"success": False, "message": edited_result}