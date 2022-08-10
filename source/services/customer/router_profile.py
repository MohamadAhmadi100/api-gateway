def get_raw_profile(customer_phone_number: dict):
    return {
            "customer": {
                "action": "get_raw_profile",
                "body": {
                    "customer_phone_number": customer_phone_number,
                }
            }
        }


def get_profile(customer_phone_number: dict):
    return {
            "customer": {
                "action": "get_profile",
                "body": {
                    "customer_phone_number": customer_phone_number,
                }
            }
        }


def edit_profile_data(customer_phone_number: dict, data: str):
    return {
            "customer": {
                "action": "edit_profile_data",
                "body": {
                    "customer_phone_number": customer_phone_number,
                    "data": data
                }
            }
        }


def change_customer_password(data: dict):
    return {
            "customer": {
                "action": "change_customer_password",
                "body": {
                    "data": data,
                }
            }
        }


def add_delivery_person(data: dict):
    return {
            "customer": {
                "action": "add_delivery_person",
                "body": {
                    "data": data,
                }
            }
        }


def get_delivery_persons(data):
    return {
            "customer": {
                "action": "get_delivery_persons",
                "body": {
                    "data": data,
                }
            }
        }


def create_informal(data: dict):
    return {
            "customer": {
                "action": "create_informal",
                "body": {
                    "data": data,
                }
            }
        }


def get_informal(data: dict):
    return {
            "customer": {
                "action": "get_informal",
                "body": {
                    "data": data,
                }
            }
        }


def get_all_informal_persons(data: dict):
    return {
            "customer": {
                "action": "get_all_informal_persons",
                "body": {
                    "data": data,
                }
            }
        }


