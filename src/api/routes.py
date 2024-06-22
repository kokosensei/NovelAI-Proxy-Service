import queue
import threading

from src.core.config import Config
from src.core.logging import setup_logger
from src.services.worker import worker_thread
from src.services.api_client import APIEndpoints

from flask import Flask, request, Response, stream_with_context

from itertools import cycle
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import requests

app = Flask(__name__)

REQUEST_QUEUES = {endpoint: queue.Queue() for endpoint in APIEndpoints}
API_SELECTOR = cycle(APIEndpoints)
LOGGER = setup_logger("APP")
CONFIG = Config()


@app.route("/ai/generate-image", methods=["GET", "POST", "PUT", "DELETE"])
def forward_request():

    LOGGER.info(
        f"\nRequest received: {request.method} {request.path} from IP: {request.remote_addr}"
    )

    auth_header = request.headers.get("Authorization")
    server_token = auth_header.split(" ")[1]

    if not auth_header or not server_token or not CONFIG.validate_token(server_token):
        return Response("Unauthorized", status=401)

    api_endpoint = next(
        API_SELECTOR
    )  # Get the next API endpoint from the round-robin selector
    q = REQUEST_QUEUES[
        api_endpoint
    ]  # Use the queue corresponding to the selected endpoint

    response_placeholder = queue.Queue(maxsize=1)

    def send_response(response: "requests.models.Response"):
        response_placeholder.put(response)

    LOGGER.info(f"Forwarding request to worker at {api_endpoint.value['url']}")
    # Forward the request to the worker
    q.put((request.method, request.full_path, request.get_data(), send_response))

    LOGGER.info("Waiting for response from worker")

    response_data = response_placeholder.get()

    if isinstance(response_data, tuple):
        # Check if it's a streaming response
        if len(response_data) == 2:
            response, content_type = response_data
            if (
                content_type == "application/x-zip-compressed"
                or content_type == "binary/octet-stream"
            ):
                # Define the generator
                def generate():
                    for chunk in response.iter_content(chunk_size=8192):
                        yield chunk

                # Use the generator for content_type application/x-zip-compressed
                return Response(
                    stream_with_context(generate()), content_type=content_type
                )
        else:
            content, status_code, content_type = response_data
            return Response(content, status=status_code, content_type=content_type)

    return Response(
        "An internal error occurred.", status=500, content_type="text/plain"
    )


def start_worker_threads():
    for endpoint in APIEndpoints:
        threading.Thread(
            target=worker_thread, args=(REQUEST_QUEUES[endpoint], endpoint), daemon=True
        ).start()
        LOGGER.info(f"Started worker thread for {endpoint.name}")
