import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.server_tokens = os.getenv("SERVER_TOKENS", "").split(",")
        self.novelai_username = os.getenv("NOVELAI_USERNAME")
        self.novelai_password = os.getenv("NOVELAI_PASSWORD")

        self.novelai_token = None

        self.API_HEADERS = {
            "Content-Type": "application/json",
            "Origin": "https://novelai.net",
            "Referer": "https://novelai.net",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        }

    def validate_token(self, token: str) -> bool:
        return token in self.server_tokens
