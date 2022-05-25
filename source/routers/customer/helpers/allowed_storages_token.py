from source.message_broker.rabbit_server import RabbitRPC


def allowed_storages(customer_id):
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

        if address.get("success"):
            default_address = None

            for addr in address.get("result", {}):
                if addr.get('isDefault'):
                    default_address = addr
                    break
            if default_address:
                if not default_address.get('cityId') == "1874":
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
                    if msm_warehouses.get("success"):
                        storage_id = msm_warehouses.get('message').get('warehouse_id')
                        return [str(storage_id), '1']
                    else:
                        return ['1']
                else:
                    return ['7']
            else:
                return []
        else:
            return []
