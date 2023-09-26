import time
import jwt
from decouple import config


JWT_SECRET = config("secret")
JWT_ALGORITHM = config("algorithm")


def signJWT(username: str):
    payload = {
        "username": username,
        "expiry": time.time() + 600
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token


def decodeJWT(token: str):
    decode_token = jwt.decode(token, JWT_SECRET, algorithm=JWT_ALGORITHM)
    try:
        return decode_token if decode_token["expires"] >= time.time() else None
    except:
        return {}