from source.helpers.case_converter import convert_case
from source.message_broker.rabbit_server import RabbitRPC
from source.routers.payment.controllers.bank_controller import saman_test
from source.routers.payment.validators.payment import SendData
from source.routers.wallet.validators.charge_wallet import Charge
from fastapi import Response, APIRouter

router = APIRouter()


@router.put("/test_wallet", tags=["test"])
def wallet_testttt(
        charge_data: Charge,
        response: Response,
):
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        wallet_response = rpc.publish(
            message={
                "wallet": {
                    "action": "create_transaction",
                    "body": {
                        "data": {
                            "customer_id": charge_data.customer_id,
                            "amount": charge_data.amount,
                            "payment_method": "online",
                            "balance": "charge",
                            "wallet_id": charge_data.wallet_id,
                            "type": "chargeWallet",
                            "action_type": "auto"
                        }
                    }
                },
            },
            headers={'wallet': True}
        ).get("wallet", {})

        if wallet_response.get("success"):
            transaction = wallet_response.get("message")
            send_data = SendData(
                amount=int(charge_data.amount)*10,
                customerId=int(charge_data.customer_id),
                serviceName="wallet",
                serviceId=f'w{transaction.get("transactionId")}',
            )
            send_data = convert_case(send_data, "snake")
            payment_result = saman_test(
                data=send_data,
                response=response
            )
            return payment_result
