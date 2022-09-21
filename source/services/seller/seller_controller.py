def seller_form_request(name: str, last_name: str, mobile_number: str, address: str, seller_status: str, shipment: str, product_warehouse: str, payment_method: str, national_id: str):
    return {
            "seller": {
                "action": "seller_form_request",
                "body": {
                    "name": name,
                    "last_name": last_name,
                    "mobile_number": mobile_number,
                    "address": address,
                    "seller_status": seller_status,
                    "shipment": shipment,
                    "product_warehouse": product_warehouse,
                    "payment_method": payment_method,
                    "national_id": national_id
                }
            }
        }


