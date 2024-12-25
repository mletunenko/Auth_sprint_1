import httpx
import pytest

from src.settings import webapp_settings
from src.utils import gen_random_email, gen_random_password

BASE_URL = f"http://{webapp_settings.service_host}:{webapp_settings.service_port}"


@pytest.fixture(scope="session")
def client():
    with httpx.Client(base_url=BASE_URL) as client:
        yield client


@pytest.fixture(scope="function")
def create_common_user(client):
    user_data = {"email": gen_random_email(),
                 "password": gen_random_password()}
    client.post("/auth/register", json=user_data)
    return user_data


@pytest.fixture(scope="function")
def create_extra_user(client):
    user_data = {"email": gen_random_email(),
                 "password": gen_random_password()}
    client.post("/auth/register", json=user_data)
    return user_data


@pytest.fixture(scope="function")
def login_common_user(client, create_common_user):
    user_data = create_common_user
    login_data = client.post("/auth/login", json=user_data).json()
    return login_data

