import time

from starlette.middleware.base import BaseHTTPMiddleware

RESPONSE_TIME = {}


class Monitoring(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request, call_next):
        start = round(time.time() * 1000)
        response = await call_next(request)
        end = round(time.time() * 1000)
        RESPONSE_TIME[request.url.path] = {
            "method": request.method,
            "value": end - start
        }
        return response

    @staticmethod
    def metric_formatter(metric_name, method, path, value):
        return f'{metric_name}{{method="{method}", path="{path}"}} {value}'

    @staticmethod
    def metrics(path):
        response = ""
        excluded_paths = ['docs/', "docs", "openapi.json", 'openapi.json/']
        for k, v in RESPONSE_TIME.items():
            if k.startswith("/" + path) and len(set([k.endswith(i) for i in excluded_paths])) != 2 and (
                    k.find("metrics") == -1
            ):
                response += Monitoring.metric_formatter("response_time", v.get("method"), k, v.get("value")) + "\n"

        return response
