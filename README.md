# NovelAI Proxy Service

## Description

This NovelAI Proxy Service is a Flask-based application that acts as an intermediary between clients and the NovelAI API. It provides a secure and efficient way to handle requests to NovelAI's image generation service, implementing features such as load balancing, automatic token refresh, and error handling.

Please consume it with [NovelAI-API-Unoffical API](https://github.com/kokosensei/NovelAI-API?tab=readme-ov-file#image-generation-unoffical-api)

## Features

- Secure proxy for NovelAI API requests
- Load balancing across multiple API endpoints
- Automatic access token refresh on 403 errors
- Request queuing and multi-threaded processing
- Comprehensive logging
- Environment-based configuration
- Token-based authentication for incoming requests

## Prerequisites

- Python 3.7+
- pip (Python package manager)

## Project Structure

```
novelai-proxy-service/
│
├── src/
│   ├── api/
│   │   └── routes.py
│   ├── core/
│   │   ├── config.py
│   │   └── logging.py
│   ├── models/
│   │   └── user.py
│   ├── services/
│   │   ├── api_client.py
│   │   └── worker.py
│   └── utils/
│       └── auth.py
├── logs/
├── .env.example
├── .gitignore
├── requirements.txt
├── setup.py
├── README.md
└── run.py
```

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/novelai-proxy-service.git
cd novelai-proxy-service
```

2. Create a virtual environment (optional but recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use venv\Scripts\activate
```

3. Install the required packages:

```bash
pip install -r requirements.txt
```

4. Set up your environment variables by creating a `.env` file in the root directory:

```
NOVELAI_USERNAME=your_username
NOVELAI_PASSWORD=your_password
SERVER_TOKENS=token1,token2,token3
NOVEL_TOKEN=your_initial_token  # Optional
```

## Usage

1. Start the server:

```bash
python run.py
```

2. The server will start on `http://127.0.0.1:5000` by default.
3. To make a request to the NovelAI API through the proxy, send your request to `http://127.0.0.1:5000/ai/generate-image`
4. make sure to include your service authentication token in the `Authorization` header.

## Configuration

- `src/core/config.py`: Contains the `Config` class for managing environment variables and application settings.
- `.env`: Store your sensitive information and configuration here.

## API Endpoints

- `/ai/generate-image`: Proxies requests to NovelAI's image generation API.

## Error Handling

- The service automatically handles 403 errors by refreshing the NovelAI access token.
- Other errors are logged and appropriate error responses are sent back to the client.

## Logging

- Logs are stored in the `logs/` directory.
- The default log file is `app.log`.
- Log rotation is implemented to manage log file sizes.

## Security

- Incoming requests are authenticated using tokens defined in the `SERVER_TOKENS` environment variable.
- NovelAI credentials are securely managed through environment variables.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

[GNU General Public License v3.0](LICENSE)

## Disclaimer

This project is not officially affiliated with NovelAI. Use at your own risk and ensure compliance with NovelAI's terms of service.