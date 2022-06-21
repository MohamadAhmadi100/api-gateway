from source.message_broker.rabbit_server import RabbitRPC


def get_allowed_storages(customer_id):
    """
    Returns a list of allowed storages for the customer.
    """
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        address = rpc.publish(
            message={
                "address": {
                    "action": "get_customer_addresses",
                    "body": {
                        "customerId": str(customer_id)
                    }
                }
            },
            headers={'address': True}
        ).get("address", {})

        if not address.get("success"):
            return []
        if not (default_address := next((addr for addr in address.get("result", {}) if addr.get('isDefault')), None)):
            return []
        if default_address.get('cityId') == "1874":
            return ['7']
        msm_warehouses = rpc.publish(
            message={
                "address": {
                    "action": "get_stock",
                    "body": {
                        "cityId": default_address.get('cityId')
                    }
                }
            },
            headers={'address': True}
        ).get("address", {})
        return [str(wms.get('warehouse_id')) for wms in msm_warehouses.get('message')] if msm_warehouses.get(
            "success") else []
