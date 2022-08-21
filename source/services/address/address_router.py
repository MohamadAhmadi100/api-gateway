def states():
    return {
            "address": {
                "action": "states",
                "body": {
                }
            }
        }


def cities(CityId):
    return {
            "address": {
                "action": "cities",
                "body": {
                    "CityId": CityId,
                }
            }
        }


def insert_address(data, customerId):
    return {
            "address": {
                "action": "insert_address",
                "body": {
                    "data": data,
                    "customerId": customerId
                }
            }
        }


def update_address(data, customerId):
    return {
            "address": {
                "action": "update_address",
                "body": {
                    "data": data,
                    "customerId": customerId
                }
            }
        }


def get_customer_addresses(customerId):
    return {
            "address": {
                "action": "get_customer_addresses",
                "body": {
                    "customerId": customerId,
                }
            }
        }


def get_default_address(customerId: str):
    return {
            "address": {
                "action": "get_default_address",
                "body": {
                    "customerId": customerId,
                }
            }
        }


def delete_customer_address(customerId: str, addressId: int):
    return {
            "address": {
                "action": "delete_customer_address",
                "body": {
                    "customerId": customerId,
                    "addressId": addressId
                }
            }
        }


def get_stock(cityId):
    return {
            "address": {
                "action": "get_stock",
                "body": {
                    "cityId": cityId,
                }
            }
        }


