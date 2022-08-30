def kowsar_transaction(order_id, price, customer_id, bank_code, bank_name):
    return {
            "kosar": {
                "action": "kowsar_transaction",
                "body": {
                    "order_id": order_id,
                    "price": price,
                    "customer_id": customer_id,
                    "bank_code": bank_code,
                    "bank_name": bank_name
                }
            }
        }


def get_kowsar_data(service_id):
    return {
            "kosar": {
                "action": "get_kowsar_data",
                "body": {
                    "service_id": service_id,
                }
            }
        }


