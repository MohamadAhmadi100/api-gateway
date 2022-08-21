def register(data: dict):
    return {
            "customer": {
                "action": "register",
                "body": {
                    "data": data,
                }
            }
        }


