import logging
from source.message_broker.rabbitmq_log import rabbit_rpc as rpc
from source.services.log import log_controller
from functools import wraps

def log_decorator(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        try:
            rpc.publish(
                [
                    log_controller.insert_log(
                        data={
                            "user_info": kwargs.get("auth_header", {})[0],
                            "service_name": "order",
                            "route_name": "final_order",
                            "service_input": {
                                "method": "PUT",
                                "body": kwargs.get("data", {}).device_type,
                                "query": "",
                            },
                            "service_output": result
                        }
                    )
                ]
            )
        except Exception as e:
            logging.error(e)

        return result
    return wrapper