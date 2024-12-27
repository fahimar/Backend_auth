Much of this code came from: https://fastapi.tiangolo.com/advanced/websockets/

# sensespeech_backend

This is the backend for the sensespeech application. It's built with FastAPI and uses SQLite for data storage.

## Installation

1.  Clone the repository:

    ```bash
    git clone <repository_url>
    ```

2.  Navigate to the project directory:

    ```bash
    cd sensespeech_backend
    ```

3.  Create and activate a virtual environment:

    - Windows:
      ```bash
      python -m venv venv
      venv\Scripts\activate
      pip install -r requirements.txt
      ```
    - macOS/Linux:
      ```bash
      python3 -m venv venv
      source venv/bin/activate
      ```

4.  Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Running the application

1.  Create the database tables:

    ```bash
    python create_tables.py
    ```

2.  Start the development server:

    ```bash
    uvicorn app:app --reload
    ```

    This will start the server at `http://127.0.0.1:8000`. You can access the API documentation at `http://127.0.0.1:8000/docs`.

## API Endpoints

- `/signup/`: Create a new user account.
- (Add other endpoints and their descriptions here)

## Contributing

(Add contribution guidelines if needed)

## License

(Add license information if needed)
