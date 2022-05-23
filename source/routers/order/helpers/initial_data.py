from starlette.exceptions import HTTPException

from source.message_broker.rabbit_server import RabbitRPC
from source.routers.cart.app import get_cart
from source.routers.customer.helpers.profile_view import get_profile_info
from source.routers.order.helpers.check_out import check_price_qty
from source.routers.order.helpers.shipment_requests import ship_address_object


# TODO full product data in cart
# TODO add stocks in cart
# TODO reciver info api


class EditQuantity:
    def __init__(self, parent_system_code, system_code, storage_id, count):
        self.parent_system_code = parent_system_code
        self.system_code = system_code
        self.storage_id = storage_id
        self.count = count

