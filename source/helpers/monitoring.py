import time
from starlette.middleware.base import BaseHTTPMiddleware
import command
from source.helpers.influx import InfluxConnection


class Monitoring(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request, call_next):
        start = round(time.time() * 1000)
        response = await call_next(request)
        end = round(time.time() * 1000)
        service = request.url.path.split("/")[1]
        if service:
            if request.path_params:
                url = "/".join(list(set(request.url.path.split("/")).difference(set(request.path_params.values()))))
            else:
                url = request.url.path
            gateway = command.run(["hostname"]).output.decode("utf-8")
            with InfluxConnection() as db:
                db.monitoring(
                    tags={
                        "service": service,
                        "url": url,
                        "method": request.method,
                        "gateway": gateway
                    },
                    fields={
                        "response_time": end - start
                    }
                )
        return response
