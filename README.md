# Network Health Monitor

A Python + Flask application that continuously pings LAN devices, stores results in SQLite, and provides a real-time web dashboard with historical charts and alerting.

## Features

- **Continuous Monitoring**: Periodically pings configured devices to check their status.
- **Real-time Dashboard**: A web interface to view device status, history, and manage devices.
- **SQLite Backend**: All data is stored in a local SQLite database.
- **REST API**: A simple API to manage devices and retrieve data.
- **Alerting**: Get notified when a device goes down (future implementation).
- **Docker Support**: Run the application in a Docker container.

## Setup and Run

### Local Development

1.  **Create a virtual environment:**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

2.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

3.  **Set environment variables:**

    ```bash
    export FLASK_APP=run.py
    ```

4.  **Initialize the database:**

    ```bash
    flask init-db
    ```

5.  **Run the application:**

    ```bash
    python run.py
    ```

    The application will be running at `http://127.0.0.1:5000`.

### Docker

1.  **Build and run the container:**

    ```bash
    docker-compose up --build
    ```

    The application will be running at `http://localhost:5000`.

## API

-   `GET /api/devices`: Get a list of all devices.
-   `POST /api/devices`: Add a new device. Requires `X-API-KEY` header.
-   `PUT /api/devices/<id>`: Update a device. Requires `X-API-KEY` header.
-   `DELETE /api/devices/<id>`: Delete a device. Requires `X-API-KEY` header.
-   `GET /api/devices/<id>/history`: Get ping history for a device.
-   `GET /api/status`: Get the current status of all devices.

### Sample Request

```bash
curl -X POST http://localhost:5000/api/devices \
-H "Content-Type: application/json" \
-H "X-API-KEY: changeme" \
-d '{"name": "Google DNS", "ip_address": "8.8.8.8"}'
```

## Testing

To run the tests, use pytest:

```bash
pytest
```
