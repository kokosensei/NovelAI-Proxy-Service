import threading
from src.api.routes import app, start_worker_threads
from src.core.logging import setup_logger

LOGGER = setup_logger("Server")

if __name__ == "__main__":
    LOGGER.info("Starting worker threads")
    threading.Thread(target=start_worker_threads, daemon=True).start()

    LOGGER.info("Starting NovelAI Proxy Service")
    app.run(host="127.0.0.1", port=5000)
