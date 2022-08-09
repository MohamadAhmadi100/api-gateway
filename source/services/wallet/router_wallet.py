def create_wallet(data: dict):
    return {
            "wallet": {
                "action": "create_wallet",
                "body": {
                    "data": data,
                }
            }
        }


def create_transaction(data: dict):
    return {
            "wallet": {
                "action": "create_transaction",
                "body": {
                    "data": data,
                }
            }
        }


def get_wallets(data: dict):
    return {
            "wallet": {
                "action": "get_wallets",
                "body": {
                    "data": data,
                }
            }
        }


def change_wallet_status(data: dict):
    return {
            "wallet": {
                "action": "change_wallet_status",
                "body": {
                    "data": data,
                }
            }
        }


def charge_wallet(data: dict):
    return {
            "wallet": {
                "action": "charge_wallet",
                "body": {
                    "data": data,
                }
            }
        }


def reserve_wallet(data: dict):
    return {
            "wallet": {
                "action": "reserve_wallet",
                "body": {
                    "data": data,
                }
            }
        }


def result_checkout(data: dict):
    return {
            "wallet": {
                "action": "result_checkout",
                "body": {
                    "data": data,
                }
            }
        }


def complete_order_wallet(data: dict):
    return {
            "wallet": {
                "action": "complete_order_wallet",
                "body": {
                    "data": data,
                }
            }
        }


def get_wallet_by_customer_id(customer_id: int):
    return {
            "wallet": {
                "action": "get_wallet_by_customer_id",
                "body": {
                    "customer_id": customer_id,
                }
            }
        }


def get_transactions(data: dict):
    return {
            "wallet": {
                "action": "get_transactions",
                "body": {
                    "data": data,
                }
            }
        }


def update_wallet(data: dict):
    return {
            "wallet": {
                "action": "update_wallet",
                "body": {
                    "data": data,
                }
            }
        }


def get_report_wallet_log(data):
    return {
            "wallet": {
                "action": "get_report_wallet_log",
                "body": {
                    "data": data,
                }
            }
        }


