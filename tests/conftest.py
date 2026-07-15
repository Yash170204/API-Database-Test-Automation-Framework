import os
import socket
import threading
import time
import pytest
import uvicorn
from typing import Generator

# Force the test database environment before importing app-level modules
TEST_DB_PATH = "test_inventory.db"
os.environ["DATABASE_PATH"] = TEST_DB_PATH

from src.app.main import app
from src.app.database import init_db
from src.api.api_client import APIClient
from src.database.db_client import DBClient
from src.utils.logger import logger

def get_free_port() -> int:
    """Find a free TCP port on local loopback."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port

@pytest.fixture(scope="session")
def server_url() -> Generator[str, None, None]:
    """Spins up the FastAPI target application in a background thread on a free port."""
    # Ensure test database is initialized
    logger.info(f"Initializing test database at: {TEST_DB_PATH}")
    init_db(TEST_DB_PATH)
    
    port = get_free_port()
    base_url = f"http://127.0.0.1:{port}"
    
    # Configure and run Uvicorn server in a background daemon thread
    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning")
    server = uvicorn.Server(config)
    
    logger.info(f"Starting local test API server at {base_url}...")
    server_thread = threading.Thread(target=server.run, daemon=True)
    server_thread.start()
    
    # Wait for server to start
    time.sleep(0.5)
    
    yield base_url
    
    # Teardown: Stop uvicorn server
    logger.info("Stopping local test API server...")
    server.should_exit = True
    server_thread.join(timeout=3)
    
    # Clean up test database file
    logger.info(f"Cleaning up test database file: {TEST_DB_PATH}")
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except Exception as e:
            logger.warning(f"Could not remove test DB file: {e}")

@pytest.fixture(scope="session")
def api_client(server_url: str) -> APIClient:
    """Provides a session-scoped API client instance."""
    return APIClient(base_url=server_url)

@pytest.fixture(scope="session")
def db_client(server_url: str) -> DBClient:
    """Provides a session-scoped DB client instance for SQL validations."""
    # Depends on server_url to ensure database path is initialized and environment set
    return DBClient(db_path=TEST_DB_PATH)

@pytest.fixture(scope="function")
def clean_db(db_client: DBClient) -> Generator[None, None, None]:
    """Fixture to ensure the database is clean before and after running a test."""
    db_client.clear_tables()
    yield
    db_client.clear_tables()
