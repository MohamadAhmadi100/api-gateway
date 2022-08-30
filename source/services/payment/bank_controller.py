def get_data(data: dict, bank_name: str):
    return {
            "payment": {
                "action": "get_data",
                "body": {
                    "data": data,
                    "bank_name": bank_name
                }
            }
        }


def redirect_url(data: dict, payment_id: int, bank_name: str):
    return {
            "payment": {
                "action": "redirect_url",
                "body": {
                    "data": data,
                    "payment_id": payment_id,
                    "bank_name": bank_name
                }
            }
        }


def callback_pay(request: str):
    return {
            "payment": {
                "action": "callback_pay",
                "body": {
                    "request": request,
                }
            }
        }


def check_verify(data: dict, token: str, bank_name: str):
    return {
            "payment": {
                "action": "check_verify",
                "body": {
                    "data": data,
                    "token": token,
                    "bank_name": bank_name
                }
            }
        }


def change_kowsar_status(kowsar_status, payment_id):
    return {
            "payment": {
                "action": "change_kowsar_status",
                "body": {
                    "kowsar_status": kowsar_status,
                    "payment_id": payment_id
                }
            }
        }


def check_closing_tabs():
    return {
            "payment": {
                "action": "check_closing_tabs",
                "body": {
                }
            }
        }


def cancel_pending_payment(service_id):
    return {
            "payment": {
                "action": "cancel_pending_payment",
                "body": {
                    "service_id": service_id,
                }
            }
        }


