# from fastapi import APIRouter, Depends
# from fastapi import Response, status
#
# from customer.models.model_register import Customer
# from customer.models.model_profile import Profile
# from customer.modules.auth import AuthHandler
# from customer.validators import validation_profile, validation_auth
#
# router_profile = APIRouter(
#     prefix="/profile",
#     tags=["profile"]
# )
#
# auth_handler = AuthHandler()
#
#
# @router_profile.get("/")
# def get_profile(
#         response: Response,
#         auth_header=Depends(auth_handler.check_current_user_tokens),
#
# ):
#     user, header = auth_header
#     profile = Profile(user)
#     result = profile.get_profile_datas()
#
#     if result:
#         response.status_code = status.HTTP_200_OK
#         return result
#     else:
#         response.status_code = status.HTTP_404_NOT_FOUND
#         message = {"massage": "اطلاعاتی برای کاربر مورد نظر وجود ندارد"}
#         return message
#
# @router_profile.put("/edit-data/")
# def edit_profile_data(
#         response: Response,
#         value:validation_profile.EditProfile,
#         # auth_header=Depends(auth_handler.check_current_user_tokens),
#
# ):
#     profile = Profile(value)
#     result = profile.update_profile()
#
#     return result
