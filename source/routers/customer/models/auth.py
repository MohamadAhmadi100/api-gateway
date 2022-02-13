from datetime import timedelta, datetime

import jwt
from fastapi import HTTPException, Header
from passlib.context import CryptContext


class AuthHandler:
    pwd_context = CryptContext(schemes=['bcrypt'], deprecated="auto")
    SECRET_KEY = "a5cad81912ad25eb12920bf6357d799773887f77291fec95c345fd136078bf2c"
    refresh_exp = timedelta(days=1)
    access_exp = timedelta(days=0, minutes=20)

    def generate_hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def verify_password(self, user_password: str, hashed_password: str) -> str:
        return self.pwd_context.verify(user_password, hashed_password)

    def encode_access_token(self, user_id: str, customer_type: str) -> str:
        pay_load = {
            'exp': datetime.utcnow() + self.access_exp,
            'iat': datetime.utcnow(),
            'sub': {"user_id": user_id, "customer_type": customer_type},
            'scope': 'access'
        }
        return jwt.encode(pay_load, self.SECRET_KEY, algorithm='HS256').decode("utf-8")

    def encode_refresh_token(self, user_id: str, customer_type: str) -> str:
        pay_load = {
            'exp': datetime.utcnow() + self.refresh_exp,
            'iat': datetime.utcnow(),
            'sub': {"user_id": user_id, "customer_type": customer_type},
            'scope': 'refresh'
        }
        return jwt.encode(pay_load, self.SECRET_KEY, algorithm='HS256').decode("utf-8")

    def decode_access_token(self, token: str) -> bool:
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return False
        except jwt.InvalidTokenError:
            return False
        else:
            return payload

    def decode_refresh_token(self, token: str):
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return False
        except jwt.InvalidTokenError:
            return False
        else:
            return payload

    def check_current_user_tokens(self, access: str = Header('access'), refresh: str = Header('refresh')):

        access_tok_payload = self.decode_access_token(access)
        refresh_tok_payload = self.decode_refresh_token(refresh)

        if access_tok_payload:
            user_name = access_tok_payload.get("sub")

            tokens = {
                "access_token_payload": access_tok_payload,
                "refresh_token_payload": refresh_tok_payload,
                "access_token": access,
                "refresh_token": refresh,
            }
            return user_name, tokens

        elif refresh_tok_payload:
            user_name = refresh_tok_payload.get("sub")
            new_access_token = self.encode_access_token(user_name.get("user_id"), user_name.get("customer_type"))
            tokens = {
                "access_token_payload": access_tok_payload,
                "refresh_token_payload": refresh_tok_payload,
                "access_token": new_access_token,
                "refresh_token": refresh,
            }
            return user_name, tokens

        else:
            raise HTTPException(status_code=401, detail={"error": "مجددا وارد شوید", "redirect": "login"})
