from source.message_broker.rabbit_server import RabbitRPC
from source.routers.cart.app import get_cart
from source.routers.customer.helpers.profile_view import get_profile_info


def ship_address_object(user, cart):
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        result = []
        rpc.response_len_setter(response_len=1)
        storage_result = rpc.publish(
            message={
                "order": {
                    "action": "shipment_storage_detail",
                    "body": {
                        "cart_data": cart,
                    }
                }
            },
            headers={"order": True}
        )

        result.append(storage_result.get("order")['message'])
        rpc.response_len_setter(response_len=1)
        address_result = rpc.publish(
            message={
                "address": {
                    "action": "get_customer_addresses",
                    "body": {
                        "customerId": str(user[0].get("user_id"))
                    }
                }},
            headers={'address': True}
        ).get("address")
        if address_result.get("success"):
            address = address_result['result']
            for items in address:
                if items.get('isDefault'):
                    address = items
                    result.append(items)
                    break
                else:
                    return {"success": False, "message": "مشتری ادرس پیش فرض ندارد"}
            stocks = []
            for items in result[0]:
                stocks.append({
                    "stockName": items['warehouse_label'],
                    "stockId": str(items['warehouse_id']),
                    "origin": items['warehouse_city_id'],
                    "destination": result[1]['cityId'],
                    "weight": 0,
                    "totalPrice": cart['totalPrice'],
                    "totalItem": 0
                })
            return_result = {
                "customerId": user[0].get("user_id"),
                "stocks": stocks,
            }
            rpc.response_len_setter(response_len=1)
            shipment_response = rpc.publish(
                message={
                    "shipment": {
                        "action": "get_shipment_details",
                        "body": {
                            "data": str(return_result)
                        }
                    }
                },
                headers={'shipment': True}
            ).get("shipment", {})['message']
            return {"success": True, "shipment_response": shipment_response, "address_response": address}
        else:
            return {"success": False, "message": "مشتری ادرس فعالی ندارد"}


def shipment_detail(auth_header, response):
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:

        cart = get_cart(response=response, auth_header=auth_header)
        if cart['products']:
            ship_address_data = ship_address_object(auth_header, cart)
            if ship_address_data.get("success"):
                customer = get_profile_info(auth_header[0])
                address = ship_address_data.get("address_response")
                shipment = ship_address_data.get("shipment_response")
                rpc.response_len_setter(response_len=1)
                reciver_info = rpc.publish(
                    message={
                        "customer": {
                            "action": "get_delivery_persons",
                            "body": {
                                "data": {
                                    "customer_phone_number": customer['customerPhoneNumber'],
                                }
                            }
                        }
                    },
                    headers={'customer': True}
                ).get("customer")
                reciver_data = []
                if reciver_info['success']:
                    reciver_data = reciver_info.get("message").get("data")

                rpc.response_len_setter(response_len=1)
                rpc.publish(
                    message={
                        "cart": {
                            "action": "remove_cart",
                            "body": {
                                "user_id": auth_header[0].get("user_id")
                            }
                        }
                    },
                    headers={'cart': True}
                ).get("cart", {})
                result = {
                    "customerData": {
                        "customerName": f'{customer["customerFirstName"]} {customer["customerLastName"]}',
                        "customerCity": customer['customerCity'],
                        "customerCityId": customer['cityID'],
                        "customerState": customer['customerProvince'],
                        "customerStateId": customer['customerProvinceCode'],
                        "CustomerAddress": address['fullAddress']
                    },
                    "shipmentDetail": shipment,
                    "reciverInfo": reciver_data,
                    "products": cart['products'],
                    "totalPrice": cart['totalPrice']

                }
                return {"success": True, "message": result, "status_code": 200}


            else:
                # shipment and address response
                return {"success": False, "message": ship_address_data.get("message"), "status_code": 404}

        else:
            # cart response
            return {"success": False, "message": "سبد خرید خالی است", "status_code": 404}


def check_shipment_per_stock(cart):
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        storage_result = rpc.publish(
            message={
                "order": {
                    "action": "shipment_storage_detail",
                    "body": {
                        "cart_data": cart,
                    }
                }
            },
            headers={"order": True}
        ).get("order").get("message")
        response = []
        for items in storage_result:
            response.append(items['warehouse_id'])
        return response