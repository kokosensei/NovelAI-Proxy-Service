import argon2
import requests

from src.models.user import User

from hashlib import blake2b
from base64 import urlsafe_b64encode


def get_access_token(user: User) -> str:
    """
    Send post request to /user/login endpoint to get user's access token.

    Returns
    -------
    `str`
        NovelAI access token which is used in the Authorization header
        with the Bearer scheme

    Raises
    ------
    `novelai.exceptions.AuthError`
        If the account credentials are incorrect
    """
    access_key = encode_access_key(user)

    response = requests.post(
        url="https://api.novelai.net/user/login",
        json={
            "key": access_key,
        },
    )

    return response.json()["accessToken"]


# https://github.com/Aedial/novelai-api/blob/main/novelai_api/utils.py
def encode_access_key(user: User) -> str:
    """
    Generate hashed access key from the user's username and password using the
    blake2 and argon2 algorithms.

    Parameters
    ----------
    user : `novelai.types.User`
        User object containing username and password

    Returns
    -------
    `str`
        Hashed access key
    """
    pre_salt = f"{user.password[:6]}{user.username}novelai_data_access_key"

    blake = blake2b(digest_size=16)
    blake.update(pre_salt.encode())
    salt = blake.digest()

    raw = argon2.low_level.hash_secret_raw(
        secret=user.password.encode(),
        salt=salt,
        time_cost=2,
        memory_cost=int(2000000 / 1024),
        parallelism=1,
        hash_len=64,
        type=argon2.low_level.Type.ID,
    )
    hashed = urlsafe_b64encode(raw).decode()

    return hashed[:64]
