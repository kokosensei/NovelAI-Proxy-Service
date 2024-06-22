import requests

from enum import Enum
from src.models.user import User
from src.core.config import Config

from src.utils.auth import get_access_token
from src.core.logging import setup_logger


class APIEndpoints(Enum):
    WEB = {"url": "https://image.novelai.net", "accept": "binary/octet-stream"}


class APIClient:
    def __init__(self, endpoint: APIEndpoints):
        self.endpoint = endpoint
        self.logger = setup_logger("API_CLIENT")

        self.config = Config()
        self.user = User(
            username=self.config.novelai_username, password=self.config.novelai_password
        )

        self.headers = self.config.API_HEADERS.copy()
        self.headers["Accept"] = endpoint.value["accept"]

        if self.config.novelai_token is None:
            self.reset_access_token()

    def update_access_token(self, token: str):
        self.headers["Authorization"] = f"Bearer {token}"

    def reset_access_token(self):
        new_token = get_access_token(self.user)
        self.update_access_token(new_token)

        self.config.novelai_token = new_token
        self.logger.info("Access token has been reset and updated.")

    def generate_image(self, method: str, url: str, data: bytes) -> requests.Response:
        if self.config.novelai_token is None:
            self.reset_access_token()

        full_url = self.endpoint.value["url"] + url
        response = requests.request(
            method=method,
            url=full_url,
            headers=self.headers,
            data=data,
            allow_redirects=False,
            stream=True,
        )
        response.raise_for_status()
        return response
