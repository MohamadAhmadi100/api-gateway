def check_is_registered(customer_phone_number: str):
    return {
            "customer": {
                "action": "check_is_registered",
                "body": {
                    "customer_phone_number": customer_phone_number,
                }
            }
        }


def send_otp_code(customer_phone_number: str):
    return {
            "customer": {
                "action": "send_otp_code",
                "body": {
                    "customer_phone_number": customer_phone_number,
                }
            }
        }


def verify_otp_code(customer_phone_number: str, customer_code: str):
    return {
            "customer": {
                "action": "verify_otp_cod",
                "body": {
                    "customer_phone_number": customer_phone_number,
                    "customer_code": customer_code
                }
            }
        }


def checking_login_otp_code(customer_phone_number: str, customer_code: str):
    return {
            "customer": {
                "action": "checking_login_otp_code",
                "body": {
                    "customer_phone_number": customer_phone_number,
                    "customer_code": customer_code
                }
            }
        }


def checking_login_password(customer_phone_number: str, customer_password: str):
    return {
            "customer": {
                "action": "checking_login_password",
                "body": {
                    "customer_phone_number": customer_phone_number,
                    "customer_password": customer_password
                }
            }
        }


def save_logout(username: dict):
    return {
            "customer": {
                "action": "save_logout",
                "body": {
                    "username": username,
                }
            }
        }


def forget_password(customer_phone_number: str, password: str):
    return {
            "customer": {
                "action": "forget_password",
                "body": {
                    "customer_phone_number": customer_phone_number,
                    "password": password
                }
            }
        }


