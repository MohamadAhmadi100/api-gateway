from source.message_broker.rabbit_server import RabbitRPC
from source.routers.cart.helpers.get_cart_helper import get_cart


def build_object(user):
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        result = []
        rpc.response_len_setter(response_len=1)
        storage_result = rpc.publish(
            message={
                "order": {
                    "action": "get_stocks",
                    "body": {
                        "cart_data": get_cart(user[0])['message'],
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
        )
        address = address_result.get("address")['result']
        for items in address:
            if items.get('isDefault'):
                result.append(items)
                break
        stocks = []
        for items in result[0]:
            stocks.append({
                "stockName": items['warehouse_label'],
                "stockId": str(items['warehouse_id']),
                "origin": result[1]['cityId'],
                "destination": items['warehouse_city_id'],
                "weight": 0,
                "totalPrice": 0,
                "totalItem": 0
            })
        return_result ={
            "customerId": user[0].get("user_id"),
            "stocks": stocks,
        }
        rpc.response_len_setter(response_len=1)
        shipment_response = rpc.publish(
            message={
                "shipment": {
                    "action": "get_shipment_details",
                    "body": {
                        "data": return_result
                    }
                }
            },
            headers={'shipment': True}
        ).get("shipment", {})

        return shipment_response
