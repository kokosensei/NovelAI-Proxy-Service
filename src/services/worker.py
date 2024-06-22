import queue
from requests.exceptions import HTTPError
from typing import Tuple, Any, TYPE_CHECKING

from src.core.logging import setup_logger
from src.services.api_client import APIClient, APIEndpoints

if TYPE_CHECKING:
    from requests.models import Response


class Worker:
    def __init__(self, request_queue: queue.Queue, api_endpoint: APIEndpoints):
        self.request_queue = request_queue
        self.api_client = APIClient(api_endpoint)
        self.logger = setup_logger("Worker")

    def run(self):
        while True:
            item = self.request_queue.get()
            if item is None:
                self.logger.info(
                    f"Shutting down worker thread for {self.api_client.endpoint.value['url']}"
                )
                break

            method, url, data, send_response = item
            try:
                response = self.process_request(method, url, data)
                send_response(response)
            except Exception as e:
                self.handle_error(e, url, send_response)
            finally:
                self.request_queue.task_done()

    def process_request(
        self, method: str, url: str, data: bytes
    ) -> Tuple[Any, int, str]:
        try:
            response = self.api_client.generate_image(method, url, data)
            return self.parse_response(response)
        except HTTPError as e:
            if e.response.status_code == 401:
                return self.handle_401_error(method, url, data)
            raise

    def parse_response(self, response: "Response") -> Tuple[Any, int, str]:
        content_type = response.headers.get("Content-Type", "")
        if content_type in ["binary/octet-stream", "application/x-zip-compressed"]:
            return response, 200, content_type
        return response.content, response.status_code, content_type

    def handle_401_error(
        self, method: str, url: str, data: bytes
    ) -> Tuple[Any, int, str]:
        self.logger.warning("Received 403 error. Attempting to reset access token.")
        self.api_client.reset_access_token()

        # Retry the request with the new access token
        response = self.api_client.generate_image(method, url, data)
        return self.parse_response(response)

    def handle_error(self, error: Exception, url: str, send_response):
        if isinstance(error, HTTPError):
            self.logger.error(f"HTTP Error for {url}: {str(error)}")
            send_response((str(error), error.response.status_code, "text/plain"))
        else:
            self.logger.error(f"Error: Request to {url} failed: {str(error)}")
            send_response((str(error), 500, "text/plain"))


def worker_thread(request_queue: queue.Queue, api_endpoint: APIEndpoints):
    Worker(request_queue, api_endpoint).run()
