import json
import logging

import requests


def decode_binary(data):
    return data.content.decode('utf-8')


def request_bank(api: str, data: dict) -> dict:

    try:
        response = requests.post(api, json=data, timeout=5, allow_redirects=True)
    except requests.Timeout:
        logging.exception("BMI time out gateway {}".format(data))
        return {"success": False, "error": "BMI time out gateway {}".format(data), "status_code": 417}
    except requests.ConnectionError:
        logging.exception("BMI time out gateway {}".format(data))
        return {"success": False, "error": "BMI time out gateway {}".format(data), "status_code": 417}
    except requests.exceptions as e:
        return {"success": False, "error": e, "status_code": 417}
    else:
        data = json.loads(decode_binary(response))
        return {"success": True, "message": data, "status_code": 204}

