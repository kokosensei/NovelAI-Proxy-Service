import queue
import requests
import logging
import threading
from itertools import cycle

from enum import Enum
from flask import Flask, request, Response, stream_with_context


NOVEL_TOKEN = ""
SERVER_TOKEN = [""]


def setupLogger():
    # Set up the root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Set up console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(console_handler)

    # Set up file handler
    file_handler = logging.FileHandler("app.log")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(file_handler)

    return logger


# Set up the root logger
logger = setupLogger()

app = Flask(__name__)

# Custom headers here
HEADERS = {
    "Content-Type": "application/json",
    "Origin": "https://novelai.net",
    "Referer": "https://novelai.net",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}


# Define Enum for API Endpoints
class APIEndpoints(Enum):
    API = {"url": "https://api.novelai.net", "accept": "application/x-zip-compressed"}
    WEB = {"url": "https://image.novelai.net", "accept": "binary/octet-stream"}


# Queues for requests to each API URL
request_queues = {endpoint: queue.Queue() for endpoint in APIEndpoints}


# Load balancing logic to cycle through the API endpoints
api_selector = cycle(APIEndpoints)


def validate_token(token):
    return token in SERVER_TOKEN


def worker(request_queue, api_endpoint):
    api_url = api_endpoint.value["url"]

    while True:
        item = request_queue.get()
        if item is None:
            logger.info(f"Shutting down worker thread for {api_url}")
            # None is used as a signal to stop the worker
            break

        method, url, data, send_response = item
        headers = HEADERS.copy()

        headers["Authorization"] = f"Bearer {NOVEL_TOKEN}"
        headers["Accept"] = api_endpoint.value["accept"]
        full_url = api_url + url

        logger.info(f"Making request to {api_url}{url}")

        try:
            # Make the request to the hidden API server
            response = requests.request(
                method=method,
                url=full_url,
                headers=headers,
                data=data,
                allow_redirects=False,
                stream=True,
            )

            response.raise_for_status()

            # Check for binary/octet-stream response
            content_type = response.headers.get("Content-Type", "")

            if (
                "binary/octet-stream" == content_type
                or "application/x-zip-compressed" == content_type
            ):

                # Just store the raw response object for later streaming
                send_response((response, content_type))
            else:
                send_response((response.content, response.status_code, content_type))

        except Exception as e:
            error_message = str(e)
            logging.error(f"Error: Request to {full_url} failed: {error_message}")
            send_response((error_message, 500, "text/plain"))

        finally:
            request_queue.task_done()


@app.route("/ai/generate-image", methods=["GET", "POST", "PUT", "DELETE"])
def forward_request():

    logger.info(
        f"\nRequest received: {request.method} {request.path} from IP: {request.remote_addr}"
    )

    auth_header = request.headers.get("Authorization")
    if not auth_header or not validate_token(auth_header.split(" ")[1]):
        return Response("Unauthorized", status=401)

    api_endpoint = next(
        api_selector
    )  # Get the next API endpoint from the round-robin selector
    q = request_queues[
        api_endpoint
    ]  # Use the queue corresponding to the selected endpoint

    response_placeholder = queue.Queue(maxsize=1)

    def send_response(response):
        response_placeholder.put(response)

    logger.info(f"Forwarding request to worker at {api_endpoint.value['url']}")
    # Forward the request to the worker
    q.put((request.method, request.full_path, request.get_data(), send_response))

    logger.info("Waiting for response from worker")

    def generate(response):  # Define the generator function in the route
        for chunk in response.iter_content(chunk_size=8192):
            yield chunk

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
    # ... existing error handling in case of unexpected response_data structure

    return Response(
        "An internal error occurred.", status=500, content_type="text/plain"
    )


if __name__ == "__main__":
    # Start worker threads
    for endpoint in APIEndpoints:
        threading.Thread(
            target=worker, args=(request_queues[endpoint], endpoint), daemon=True
        ).start()

    logger.info("Starting Flask proxy application")

    app.run(port=5000)
