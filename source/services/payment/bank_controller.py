def get_data(data, bank_name):
    return {
            "payment": {
                "action": "get_data",
                "body": {
                    "data": data,
                    "bank_name": bank_name
                }
            }
        }


def redirect_url(data, payment_id, bank_name):
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


def callback_pay(request):
    return {
            "payment": {
                "action": "callback_pay",
                "body": {
                    "request": request,
                }
            }
        }


def check_verify(data, token, bank_name):
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


