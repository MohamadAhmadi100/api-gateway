# from fastapi import APIRouter, Depends
# from fastapi import Response, status
# from source.message_broker.rabbit_server import RabbitRPC

# from source.routers.customer.module.auth import AuthHandler
# from source.routers.customer.validators import validation_profile, validation_auth

# router_profile = APIRouter(
#     prefix="/profile",
#     tags=["profile"]
# )

# custom_attribute = {
#     "customerFirstName": {
#         "name": "customerFirstName",
#         "label": "نام",
#         "customer_type": "any",
#         "input_type": "string",
#         "required": True,
#         "ecommerce_use_in_filter": False,
#         "portal_use_in_filter": True,
#         "portal_use_in_search": True,
#         "ecommerce_use_in_search": False,
#         "show_in_portal": True,
#         "show_in_ecommerce": True,
#         "editable_in_portal": True,
#         "editable_in_ecommerce": True,
#         "regex": "^[\u0600-\u06FF ]{2,32}$",
#         "order": 1,
#         "parent": None,
#         "default_value": None,
#         "default_value_label": None,
#         "values": None,
#         "values_label": None,
#         "set_to_nodes": False
#     },
#     "customerPhoneNumber": {
#         "name": "customerPhoneNumber",
#         "label": "موبایل",
#         "customer_type": "B2C",
#         "input_type": "string",
#         "required": True,
#         "ecommerce_use_in_filter": False,
#         "portal_use_in_filter": True,
#         "portal_use_in_search": True,
#         "ecommerce_use_in_search": False,
#         "show_in_portal": True,
#         "show_in_ecommerce": True,
#         "editable_in_portal": False,
#         "editable_in_ecommerce": False,
#         "regex": "^09[0-9]{9}$",
#         "order": 3,
#         "parent": None,
#         "default_value": "09129999999",
#         "default_value_label": None,
#         "values": None,
#         "values_label": None,
#         "set_to_nodes": False
#     },
#     "customerLastName": {
#         "name": "customerLastName",
#         "label": "نام خانوادگی",
#         "customer_type": "any",
#         "input_type": "string",
#         "required": False,
#         "ecommerce_use_in_filter": False,
#         "portal_use_in_filter": True,
#         "ecommerce_use_in_search": False,
#         "portal_use_in_search": True,
#         "show_in_portal": True,
#         "show_in_ecommerce": True,
#         "editable_in_portal": True,
#         "editable_in_ecommerce": True,
#         "order": 2,
#         "regex": "[\u0600-\u06FF ]{2,32}$",
#         "parent": "",
#         "default_value": None,
#         "default_value_label": None,
#         "values": None,
#         "values_label": None,
#         "set_to_nodes": False
#     },
#     "customerNationalID": {
#         "name": "customerNationalID",
#         "label": "کد ملی",
#         "customer_type": "any",
#         "input_type": "string",
#         "required": False,
#         "ecommerce_use_in_filter": False,
#         "portal_use_in_filter": True,
#         "ecommerce_use_in_search": False,
#         "portal_use_in_search": True,
#         "show_in_portal": True,
#         "show_in_ecommerce": True,
#         "editable_in_portal": True,
#         "editable_in_ecommerce": False,
#         "order": 4,
#         "regex": "^[0-9]{10}$",
#         "parent": None,
#         "default_value": "1104444444",
#         "default_value_label": None,
#         "values": None,
#         "values_label": None,
#         "set_to_nodes": False
#     },
#     "customerIsMobileConfirm": {
#         "name": "customerIsMobileConfirm",
#         "label": "تایید شماره موبایل",
#         "customer_type": "any",
#         "input_type": "boolean",
#         "required": False,
#         "ecommerce_use_in_filter": False,
#         "portal_use_in_filter": True,
#         "ecommerce_use_in_search": False,
#         "portal_use_in_search": True,
#         "show_in_portal": True,
#         "show_in_ecommerce": True,
#         "editable_in_portal": False,
#         "editable_in_ecommerce": False,
#         "order": 5,
#         "regex": None,
#         "parent": None,
#         "default_value": False,
#         "default_value_label": None,
#         "values": None,
#         "values_label": None,
#         "set_to_nodes": False
#     },
#     "customerIsConfirm": {
#         "name": "customerIsConfirm",
#         "label": "تایید مشتری",
#         "customer_type": "any",
#         "input_type": "boolean",
#         "required": False,
#         "ecommerce_use_in_filter": False,
#         "portal_use_in_filter": True,
#         "ecommerce_use_in_search": False,
#         "portal_use_in_search": True,
#         "show_in_portal": True,
#         "show_in_ecommerce": True,
#         "editable_in_portal": False,
#         "editable_in_ecommerce": False,
#         "order": 6,
#         "regex": None,
#         "parent": None,
#         "default_value": False,
#         "default_value_label": None,
#         "values": None,
#         "values_label": None,
#         "set_to_nodes": False
#     },
#     "customerIsActive": {
#         "name": "customerIsActive",
#         "label": "وضعیت",
#         "customer_type": "any",
#         "input_type": "boolean",
#         "required": False,
#         "ecommerce_use_in_filter": False,
#         "portal_use_in_filter": True,
#         "ecommerce_use_in_search": False,
#         "portal_use_in_search": True,
#         "show_in_portal": True,
#         "show_in_ecommerce": True,
#         "editable_in_portal": False,
#         "editable_in_ecommerce": False,
#         "order": 7,
#         "regex": None,
#         "parent": None,
#         "default_value": False,
#         "default_value_label": None,
#         "values": None,
#         "values_label": None,
#         "set_to_nodes": False
#     },
#     "customerType": {
#         "name": "customerType",
#         "label": "نوع مشتری",
#         "customer_type": "any",
#         "input_type": "boolean",
#         "required": False,
#         "ecommerce_use_in_filter": False,
#         "portal_use_in_filter": True,
#         "ecommerce_use_in_search": False,
#         "portal_use_in_search": True,
#         "show_in_portal": True,
#         "show_in_ecommerce": True,
#         "editable_in_portal": True,
#         "editable_in_ecommerce": False,
#         "order": 8,
#         "regex": None,
#         "parent": None,
#         "default_value": ['B2C'],
#         "default_value_label": ["عمده فروش"],
#         "values": None,
#         "values_label": None,
#         "set_to_nodes": False
#     },
#     "customerEmail": {
#         "name": "customerEmail",
#         "label": "ایمیل",
#         "customer_type": "any",
#         "input_type": "email",
#         "required": True,
#         "ecommerce_use_in_filter": False,
#         "portal_use_in_filter": True,
#         "ecommerce_use_in_search": False,
#         "portal_use_in_search": True,
#         "show_in_portal": True,
#         "show_in_ecommerce": True,
#         "editable_in_portal": True,
#         "editable_in_ecommerce": True,
#         "order": 6,
#         "regex": "[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}",
#         "parent": None,
#         "default_value": None,
#         "default_value_label": None,
#         "values": None,
#         "values_label": None,
#         "set_to_nodes": False
#     },
#     "customerShopName": {
#         "name": "customerShopName",
#         "label": "نام شرکت/مغازه",
#         "customer_type": "B2B",
#         "input_type": "string",
#         "required": False,
#         "ecommerce_use_in_filter": False,
#         "portal_use_in_filter": True,
#         "ecommerce_use_in_search": False,
#         "portal_use_in_search": True,
#         "show_in_portal": True,
#         "show_in_ecommerce": True,
#         "editable_in_portal": True,
#         "editable_in_ecommerce": True,
#         "order": 10,
#         "regex": "[\u0600-\u06FF ]{2,32}$",
#         "parent": None,
#         "default_value": None,
#         "default_value_label": None,
#         "values": None,
#         "values_label": None,
#         "set_to_nodes": False
#     },
#     "customerAccountNumber": {
#         "name": "customerAccountNumber",
#         "label": "شماره حساب",
#         "customer_type": "B2C",
#         "input_type": "string",
#         "required": False,
#         "ecommerce_use_in_filter": False,
#         "portal_use_in_filter": False,
#         "ecommerce_use_in_search": False,
#         "portal_use_in_search": False,
#         "show_in_portal": True,
#         "show_in_ecommerce": True,
#         "editable_in_portal": True,
#         "editable_in_ecommerce": True,
#         "order": 7,
#         "regex": None,
#         "parent": None,
#         "default_value": None,
#         "default_value_label": None,
#         "values": None,
#         "values_label": None,
#         "set_to_nodes": False
#     },
#     "customerCrateTime": {
#         "name": "customerCrateTime",
#         "label": "تاریخ ثبت نام",
#         "customer_type": "any",
#         "input_type": "integer",
#         "required": False,
#         "ecommerce_use_in_filter": False,
#         "portal_use_in_filter": True,
#         "ecommerce_use_in_search": False,
#         "portal_use_in_search": True,
#         "show_in_portal": True,
#         "show_in_ecommerce": True,
#         "editable_in_portal": False,
#         "editable_in_ecommerce": False,
#         "order": 0,
#         "regex": None,
#         "parent": None,
#         "default_value": None,
#         "default_value_label": None,
#         "values": None,
#         "values_label": None,
#         "set_to_nodes": False
#     },
#     "customerTelephoneNumber": {
#         "name": "customerTelephoneNumber",
#         "label": "تلفن ثابت",
#         "customer_type": "B2B",
#         "input_type": "string",
#         "required": False,
#         "ecommerce_use_in_filter": False,
#         "portal_use_in_filter": True,
#         "ecommerce_use_in_search": False,
#         "portal_use_in_search": True,
#         "show_in_portal": True,
#         "show_in_ecommerce": True,
#         "editable_in_portal": True,
#         "editable_in_ecommerce": True,
#         "order": 5,
#         "regex": None,
#         "parent": None,
#         "default_value": "02188887799",
#         "default_value_label": None,
#         "values": None,
#         "values_label": None,
#         "set_to_nodes": False
#     },
#     "customerShopStatus": {
#         "name": "customerShopStatus",
#         "label": "وضعیت فروشگاه",
#         "customer_type": "B2B",
#         "input_type": "checkBox",
#         "required": False,
#         "ecommerce_use_in_filter": False,
#         "portal_use_in_filter": True,
#         "ecommerce_use_in_search": False,
#         "portal_use_in_search": True,
#         "show_in_portal": True,
#         "show_in_ecommerce": True,
#         "editable_in_portal": True,
#         "editable_in_ecommerce": True,
#         "order": 8,
#         "regex": None,
#         "parent": None,
#         "default_value": "owner",
#         "default_value_label": "مالک",
#         "values": [{"name": "owner", "label": "مالک"}, {"name": "rent", "label": "استیجاری"},
#                    {"name": "mortgage", "label": "رهن"}],
#         "set_to_nodes": False,
#     },
#     "customerShopLocation": {
#         "name": "customerShopLocation",
#         "label": "موقعیت مکانی فروشگاه",
#         "customer_type": "B2B",
#         "input_type": "dropDown",
#         "required": False,
#         "ecommerce_use_in_filter": False,
#         "portal_use_in_filter": True,
#         "ecommerce_use_in_search": False,
#         "portal_use_in_search": True,
#         "show_in_portal": True,
#         "show_in_ecommerce": True,
#         "editable_in_portal": True,
#         "editable_in_ecommerce": True,
#         "order": 9,
#         "regex": None,
#         "parent": None,
#         "default_value": "street",
#         "default_value_label": "خیابان",
#         "values": [{"name": "passage", "label": "پاساژ"}],
#         "set_to_nodes": False,
#     },
#     "customerEducation": {
#         "name": "customerEducation",
#         "label": "تحصیلات",
#         "customer_type": "any",
#         "input_type": "dropDown",
#         "required": False,
#         "ecommerce_use_in_filter": False,
#         "portal_use_in_filter": True,
#         "ecommerce_use_in_search": False,
#         "portal_use_in_search": True,
#         "show_in_portal": True,
#         "show_in_ecommerce": True,
#         "editable_in_portal": True,
#         "editable_in_ecommerce": True,
#         "order": 9,
#         "regex": None,
#         "parent": None,
#         "default_value": "owner",
#         "default_value_label": "دیپلم",
#         "values": [{"name": "diploma", "label": "دیپلم"}, {"name": "postgraduate", "label": "کاردانی"},
#                    {"name": "bachelor", "label": "کارشناسی"},
#                    {"name": "master", "label": "کارشناسی ارشد"}, {"name": "doctorate", "label": "دکتری"}],
#         "values_label": ["دیپلم", "کاردانی", "کارشناسی", "کارشناسی ارشد", "دکتری"],
#         "set_to_nodes": False,
#     },
#     "customerImage": {
#         "name": "customerImage",
#         "label": "عکس",
#         "customer_type": "any",
#         "input_type": "mediaImage",
#         "required": False,
#         "ecommerce_use_in_filter": False,
#         "portal_use_in_filter": False,
#         "ecommerce_use_in_search": False,
#         "portal_use_in_search": False,
#         "show_in_portal": True,
#         "show_in_ecommerce": True,
#         "editable_in_portal": True,
#         "editable_in_ecommerce": True,
#         "order": 0,
#         "regex": None,
#         "parent": None,
#         "default_value": "/src/default.png",
#         "default_value_label": "دیپلم",
#         "values": None,
#         "values_label": None,
#         "set_to_nodes": False,
#     },
#     "customerDocuments": {
#         "name": "customerDocuments",
#         "label": "مدارک",
#         "customer_type": "any",
#         "input_type": "mediaImage",
#         "required": False,
#         "ecommerce_use_in_filter": False,
#         "portal_use_in_filter": False,
#         "ecommerce_use_in_search": False,
#         "portal_use_in_search": False,
#         "show_in_portal": True,
#         "show_in_ecommerce": True,
#         "editable_in_portal": True,
#         "editable_in_ecommerce": True,
#         "order": 0,
#         "regex": None,
#         "parent": None,
#         "default_value": "/src/default.png",
#         "default_value_label": "دیپلم",
#         "values": None,
#         "values_label": None,
#         "set_to_nodes": False,
#     }
# }

# auth_handler = AuthHandler()

# rpc = RabbitRPC(exchange_name='headers_exchange', timeout=5)
# rpc.connect()
# rpc.consume()


# @router_profile.get("/")
# def get_profile(
#         response: Response,
#         auth_header=Depends(auth_handler.check_current_user_tokens),
# ):
#     customer_phone_number, header = auth_header
#     rpc.response_len_setter(response_len=1)
#     result = rpc.publish(
#         message={
#             "customer": {
#                 "action": "get_profile",
#                 "body": {
#                     "customer_phone_number": customer_phone_number,
#                 }
#             }
#         },
#         headers={'customer': True}
#     )
#     customer_result = result.get("customer", {})
#     if result.get("success"):
#         for attr, value in result.items():
#             if custom_attribute.get(attr):
#                 custom_attribute[attr]["value"] = value
#         response.status_code = status.HTTP_200_OK
#         response.headers["accessToken"] = header.get("access_token")
#         response.headers["refresh_token"] = header.get("refresh_token")
#         return custom_attribute
#     response.status_code = status.HTTP_404_NOT_FOUND
#     message = {"massage": "اطلاعاتی برای کاربر مورد نظر وجود ندارد"}
#     return message


# @router_profile.put("/")
# def edit_profile_data(
#         response: Response,
#         value: validation_profile.EditProfile,
#         auth_header=Depends(auth_handler.check_current_user_tokens),

# ):
#     customer_phone_number, header = auth_header
#     if customer_phone_number:
#         profile = Profile(customer_phone_number)
#         result = profile.update_profile(value)
#         response.status_code = status.HTTP_200_OK
#         response.headers["accessToken"] = header.get("access_token")
#         response.headers["refresh_token"] = header.get("refresh_token")
#         return result
#     response.status_code = status.HTTP_404_NOT_FOUND
#     message = {"massage": "اطلاعاتی برای کاربر مورد نظر وجود ندارد"}
#     return message


# @router_profile.put("/change-password")
# def change_customer_password(
#         response: Response,
#         data: validation_profile.ChangePassword,
#         auth_header=Depends(auth_handler.check_current_user_tokens),
# ):
#     response.status_code = status.HTTP_202_ACCEPTED
#     phone_number, token_dict = auth_header
#     customer = Customer(phone_number)
#     profile = Profile(customer)
#     result = profile.change_password(data)
#     if result:
#         response.status_code = status.HTTP_200_OK
#         response.headers["accessToken"] = token_dict.get("access_token")
#         response.headers["refresh_token"] = token_dict.get("refresh_token")
#         message = {
#             "massage": "رمز عبور با موفقیت بروز شد",
#         }
#         return message
#     response.status_code = status.HTTP_406_NOT_ACCEPTABLE
#     response.headers["accessToken"] = token_dict.get("access_token")
#     response.headers["refresh_token"] = token_dict.get("refresh_token")
#     message = {
#         "massage": "رمز وارد شده صحیح نمی باشد",
#     }
#     return message
