import json
import logging
from zeep import Transport, Client
import requests


def decode_binary(data):
    return data.content.decode('utf-8')


def request_bank_handler(api: str, data: dict, bank_name: str):
    handler = {
        "melli": post_request,
        "mellat": mellat_handler,
        "saman": post_request
    }
    return handler[bank_name](api, data)


def mellat_handler(step: str, data: dict):
    if step == "redirect":
        redirect = soap_request("bpPayRequest", data)
        return {"response": True, "message": redirect.get("message")}
    if step == "verify":
        verify = soap_request("bpVerifyRequest", data)
        settle = soap_request("bpSettleRequest", data)
        if verify.get("message") != "0":
            return {"response": False, "error": verify}
        elif settle.get("message") != "0":
            return {"response": False, "error": verify}
        return {
            "response": True,
            "message": {
                "verify_result": verify.get("message"),
                "settle": settle.get("message")
            }
        }


response = {}


def soap_request(method: str, data: dict):
    global response
    try:
        transport = Transport(timeout=10, operation_timeout=10)
        client = Client('https://bpm.shaparak.ir/pgwchannel/services/pgw?wsdl', transport=transport)
        exec(f"global response ; response = client.service.{method}(**{data})")
    except TimeoutError:
        logging.exception("Mellat time out gateway {}".format(data))
        return {"response": False, "error": "Mellat time out gateway {}".format(data)}
    except ConnectionError:
        logging.exception("Mellat time out gateway {}".format(data))
        return {"response": False, "error": "Mellat connection error gateway {}".format(data)}
    except Exception as e:
        return {"response": False, "error": f"wtf{e}"}
    else:
        return {"response": True, "message": response}


def post_request(api: str, data: dict) -> dict:
    try:
        post_response = requests.post(api, json=data, timeout=10, allow_redirects=True)
    except requests.Timeout as e:
        logging.exception("bank time out gateway {}".format(e))
        return {"response": False, "error": "bank time out gateway {}".format(e)}
    except requests.ConnectionError as e:
        logging.exception("bank time out gateway {}".format(e))
        return {"response": False, "error": "bank connection error gateway {}".format(e)}
    except requests.exceptions as e:
        return {"response": False, "error": e}
    else:
        data = json.loads(decode_binary(post_response))
        return {"response": True, "message": data}
