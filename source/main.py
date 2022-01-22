import uvicorn
from fastapi import FastAPI, status, responses, exceptions
from source.routers.cart.app import cart

app = FastAPI(title="API Gateway",
              description="""
        An application for API management that sits between a client and a collection of backend services. This application acts as a reverse proxy to accept all application programming interface (API) calls, aggregate the various services required to fulfill them, and return the appropriate result.
    """,
              version="0.0.1",
              # openapi_tags=tags,
              default_response_class=responses.ORJSONResponse
              )

# ----------------------------------------- Mount all services here -------------------------------------------------- #

app.mount("/cart", cart)

# ----------------------------------------- Mount all services here -------------------------------------------------- #


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
