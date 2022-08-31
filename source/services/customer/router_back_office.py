def get_customers_grid_data(data: str):
    return {
            "customer": {
                "action": "get_customers_grid_data",
                "body": {
                    "data": data,
                }
            }
        }


def crm_get_profile(customer_phone_number: dict):
    return {
            "customer": {
                "action": "crm_get_profile",
                "body": {
                    "customer_phone_number": customer_phone_number,
                }
            }
        }


def set_confirm_status(mobileNumber: str):
    return {
            "customer": {
                "action": "set_confirm_status",
                "body": {
                    "mobileNumber": mobileNumber,
                }
            }
        }


def set_cancel_status(mobileNumber: str):
    return {
            "customer": {
                "action": "set_cancel_status",
                "body": {
                    "mobileNumber": mobileNumber,
                }
            }
        }


def set_kosar_data(mobileNumber, kosarData):
    return {
            "customer": {
                "action": "set_kosar_data",
                "body": {
                    "mobileNumber": mobileNumber,
                    "kosarData": kosarData
                }
            }
        }


def edit_customers_grid_data(data):
    return {
            "customer": {
                "action": "edit_customers_grid_data",
                "body": {
                    "data": data,
                }
            }
        }


def get_informal_flag(mobileNumber: str):
    return {
            "customer": {
                "action": "get_informal_flag",
                "body": {
                    "mobileNumber": mobileNumber,
                }
            }
        }


def set_informal_flag(mobileNumber: str, customerHasInformal: bool):
    return {
            "customer": {
                "action": "set_informal_flag",
                "body": {
                    "mobileNumber": mobileNumber,
                    "customerHasInformal": customerHasInformal
                }
            }
        }


def get_customer_data_by_id(id_list: list):
    return {
            "customer": {
                "action": "get_customer_data_by_id",
                "body": {
                    "id_list": id_list,
                }
            }
        }


def search_customers_by_name(phrase: str):
    return {
            "customer": {
                "action": "search_customers_by_name",
                "body": {
                    "phrase": phrase,
                }
            }
        }


