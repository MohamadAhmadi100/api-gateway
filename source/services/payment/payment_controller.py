def get_all_payment_by_service_id(service_id):
    return {
            "payment": {
                "action": "get_all_payment_by_service_id",
                "body": {
                    "service_id": service_id,
                }
            }
        }


def get_payment_by_service_id(service_id):
    return {
            "payment": {
                "action": "get_payment_by_service_id",
                "body": {
                    "service_id": service_id,
                }
            }
        }


def get_payment(per_page, page, filters):
    return {
            "payment": {
                "action": "get_payment",
                "body": {
                    "per_page": per_page,
                    "page": page,
                    "filters": filters
                }
            }
        }


