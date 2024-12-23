import httpx
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

BASE_URL = "http://localhost:8000"
DATABASE_URL = "postgresql://user:password@localhost:5432/auth-test"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def client():
    with httpx.Client(base_url=BASE_URL) as client:
        yield client


@pytest.fixture(scope="function")
def create_common_user(client):
    user_data = {
        "email": "test@example.com", "password": "securepassword"
    }
    client.post("/auth/register", json=user_data)
    return user_data


@pytest.fixture(scope="function")
def create_extra_user(client):
    user_data = {
        "email": "extra@example.com", "password": "extrasecurepassword"
    }
    client.post("/auth/register", json=user_data)
    return user_data


@pytest.fixture(scope="function")
def login_common_user(client, create_common_user):
    user_data = create_common_user
    login_data = client.post("/auth/login", json=user_data).json()
    return login_data


@pytest.fixture(scope="function")
def clear_database():
    with engine.connect() as connection:
        connection.execute(text("TRUNCATE TABLE users CASCADE;"))
        connection.execute(text("TRUNCATE TABLE roles CASCADE;"))
        connection.execute(text("TRUNCATE TABLE login_history CASCADE;"))
        connection.commit()
    yield
