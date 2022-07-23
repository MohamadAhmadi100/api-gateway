def get_customer_kosar_data(data: dict):
    return {
            "kosar": {
                "action": "get_customer_kosar_data",
                "body": {
                    "data": data,
                }
            }
        }


