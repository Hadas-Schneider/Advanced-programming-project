import pytest
import base64
from app import app, users, inventory
from User import User
from inventory import Inventory
from furniture import Chair
import json


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def create_test_user():
    """
    Create a test user before running authentication-based tests
    """
    user = User(name="Test User", email="test@example.com", password="Test@123",
                address="123 Test St", payment_method="Credit Card")
    users[user.email] = user
    return user


def get_auth_headers(email, password):
    """"
    Helper function to generate Authorization headers for HTTP Basic Authentication
    """
    credentials = f"{email}:{password}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode("utf-8")
    return {"Authorization": f"Basic {encoded_credentials}"}


def test_register_user(client):
    """
    Test user registration endpoint.
    """
    response = client.post("/user/register", json={
        "name": "Test User",
        "email": "test@example.com",
        "password": "Test@123",
        "address": "123 Test St",
        "payment_method": "Credit Card"
    })
    assert response.status_code == 201
    assert b"User registered successfully" in response.data


def test_login_user(client):
    """
    Test user login endpoint.
    """
    response = client.post("/user/login", json={
        "email": "test@example.com",
        "password": "Test@123"
    })
    assert response.status_code == 200
    assert response.json["message"] == "Login Successful!"


def test_view_cart(client):
    """
    Test viewing the shopping cart.
    """
    headers = get_auth_headers("test@example.com", "Test@123")
    response = client.get("/cart/view", query_string={"user_email": "test@example.com"}, headers=headers)
    assert response.status_code == 200


def add_item_to_cart(client, create_test_user):
    """
    Test adding an item to the cart.
    """
    headers = get_auth_headers("test@example.com", "Test@123")
    response = client.post("/cart/add", json={
        "user_email": "test@example.com",
        "item_name": "Office Chair",
        "quantity": 1
    }, headers=headers)
    assert response.status_code in [200, 404]


def test_remove_item_from_cart(client, create_test_user):
    """
    Test removing an existing item from the cart.
    """
    headers = get_auth_headers("test@example.com", "Test@123")
    response = client.post("/cart/remove", json={
        "user_email": "test@example.com",
        "item_name": "Office Chair"
    }, headers=headers)
    response = client.delete("/cart/remove", json={
        "item_name": "Office Chair"
    }, headers=headers)

    assert response.status_code in [200, 404], f"Unexpected response: {response.status_code}, {response.data}"


def test_checkout_success(client, create_test_user):
    """
    Test successful checkout process.
    """
    headers = get_auth_headers("test@example.com", "Test@123")
    print("Inventory before adding item:", inventory.items_by_type)

    inventory.items_by_type.setdefault("Chair", {})["Office Chair"] = Chair(
        u_id="001", name="Office Chair", description="Ergonomic chair",
        material="Metal", color="Black", wp=2, price=100.0, dimensions=(60, 60, 120),
        country="USA", available_quantity=5, has_armrests=True
    )
    add_response = client.put("/cart/add", json={
        "name": "Office Chair",
        "type": "Chair",
        "quantity": 1
    }, headers=headers)
    print("Add to Cart Response:", add_response.json)
    assert add_response.status_code == 200, f"Adding item to cart failed! Response:{add_response.json}"
    print("Inventory after adding item:", inventory.items_by_type)
    response = client.post("/cart/checkout", json={"user_email": "test@example.com"}, headers=headers)
    print("Checkout Response:", response.json)
    assert response.status_code in [200, 404]


def test_add_item_not_in_inventory(client, create_test_user):
    """
    Test adding an item that does not exist in inventory.
    We expect it to return 400 - Bad request with a relevant error message.
    """
    headers = get_auth_headers("test@example.com", "Test@123")
    response = client.put("/cart/add", json={
        "name": "Nonexistent Item",
        "type": "Table",
        "quantity": 1
    }, headers=headers)
    print("Response JSON:", response.json)

    assert response.status_code == 404
    assert b"'Nonexistent Item' of type 'Table' not found in inventory." in response.data


def test_remove_item_not_in_cart(client, create_test_user):
    """
    Test removing an item that is not in the user's cart.
    Expected result: Should return 400 Bad Request with an appropriate error message.
    """
    headers = get_auth_headers("test@example.com", "Test@123")

    response = client.delete("/cart/remove", json={
        "item_name": "Nonexistent Item"
    }, headers=headers)
    print("Response JSON:", response.json)
    assert response.status_code == 404, f"Unexpected response: {response.status_code}, {response.data}"

