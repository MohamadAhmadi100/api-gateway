from datetime import timedelta, datetime
from typing import Union, Any, Optional

import jwt
from fastapi import HTTPException, Header
from jwt import exceptions as jwt_exceptions
from passlib.context import CryptContext

from source.config import settings


class AuthHandler:
    pwd_context = CryptContext(schemes=['bcrypt'], deprecated="auto")
    SECRET_KEY = settings.SECRET_KEY
    refresh_exp = timedelta(days=20)
    access_exp = timedelta(days=0, minutes=20)

    def generate_hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def verify_password(self, user_password: str, hashed_password: str) -> str:
        return self.pwd_context.verify(user_password, hashed_password)

    def encode_access_token(self, sud_dict: dict) -> str:
        pay_load = {
            'exp': datetime.utcnow() + self.access_exp,
            'iat': datetime.utcnow(),
            'sub': sud_dict,
            'scope': 'access',
            "expired": False
        }
        return jwt.encode(pay_load, self.SECRET_KEY, algorithm='HS256')

    def encode_refresh_token(self, sub_dict: dict) -> str:
        pay_load = {
            'exp': datetime.utcnow() + self.refresh_exp,
            'iat': datetime.utcnow(),
            'sub': sub_dict,
            'scope': 'refresh',
            "expired": False
        }
        return jwt.encode(pay_load, self.SECRET_KEY, algorithm='HS256')

    def decode_access_token(self, token: str) -> Union[Optional[bool], Any]:
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=["HS256"])
        except jwt_exceptions.ExpiredSignatureError:
            return None

        except jwt_exceptions.InvalidSignatureError:
            return False

        except jwt_exceptions.InvalidAlgorithmError:
            return False

        except jwt_exceptions.InvalidTokenError:
            return False

        else:
            return payload if payload.get("scope") == "access" and not payload.get("expired") else False

    def decode_refresh_token(self, token: str):
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=["HS256"])

        except jwt_exceptions.ExpiredSignatureError:
            return None

        except jwt_exceptions.InvalidSignatureError:
            return False

        except jwt_exceptions.InvalidAlgorithmError:
            return False

        except jwt_exceptions.InvalidTokenError:
            return False

        else:
            return payload if payload.get("scope") == "refresh" else False

    def check_current_user_tokens(self, access: str = Header(...), refresh: str = Header(...)):

        access = access.replace(" ", "")
        refresh = refresh.replace(" ", "")
        access_tok_payload = self.decode_access_token(access)
        refresh_tok_payload = self.decode_refresh_token(refresh)

        # for invalid token
        if access_tok_payload is False:
            raise HTTPException(status_code=401, detail={"error": "مجددا وارد شوید", "redirect": "login"})

        if access_tok_payload:
            user_data = access_tok_payload.get("sub")
            tokens = {
                "access_token_payload": access_tok_payload,
                "refresh_token_payload": refresh_tok_payload,
                "access_token": access,
                "refresh_token": refresh,
            }
            return user_data, tokens

        elif access_tok_payload is None and refresh_tok_payload:
            user_data = refresh_tok_payload.get("sub")
            new_access_token = self.encode_access_token(user_data)
            tokens = {
                "access_token_payload": access_tok_payload,
                "refresh_token_payload": refresh_tok_payload,
                "access_token": new_access_token,
                "refresh_token": refresh,
            }
            return user_data, tokens

        else:
            raise HTTPException(status_code=401, detail={"error": "مجددا وارد شوید", "redirect": "login"})

    def expire_token(self, access_token: str, refresh_token: str):
        try:
            access_payload = jwt.decode(access_token, self.SECRET_KEY, algorithms=["HS256"])
            refresh_payload = jwt.decode(refresh_token, self.SECRET_KEY, algorithms=["HS256"])
        except Exception:
            pass
