import json

from fastapi import Response, Depends, HTTPException
from fastapi import status, APIRouter

from source.message_broker.rabbit_server import RabbitRPC
from source.routers.customer.module.auth import AuthHandler
from source.routers.customer.validators import validation_auth
