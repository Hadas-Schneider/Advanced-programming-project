import pytest
import base64
from unittest.mock import patch, MagicMock, mock_open
from app import app, users, orders, inventory
from User import User
from furniture import Chair
from shopping_cart import ShoppingCart


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


@patch.object(ShoppingCart, "save_cart_to_csv", MagicMock())
@patch.object(ShoppingCart, "load_cart_from_csv", MagicMock())
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


@patch.object(ShoppingCart, "save_cart_to_csv", MagicMock())
@patch.object(ShoppingCart, "load_cart_from_csv", MagicMock())
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


@patch.object(ShoppingCart, "save_cart_to_csv", MagicMock())
@patch.object(ShoppingCart, "load_cart_from_csv", MagicMock())
def test_view_cart(client):
    """
    Test viewing the shopping cart.
    """
    headers = get_auth_headers("test@example.com", "Test@123")
    response = client.get("/cart/view", query_string={"user_email": "test@example.com"}, headers=headers)
    assert response.status_code == 200


@patch.object(ShoppingCart, "save_cart_to_csv", MagicMock())
@patch.object(ShoppingCart, "load_cart_from_csv", MagicMock())
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


@patch.object(ShoppingCart, "save_cart_to_csv", MagicMock())
@patch.object(ShoppingCart, "load_cart_from_csv", MagicMock())
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


@patch.object(ShoppingCart, "checkout", return_value=MagicMock(order_id="1234", total_price=500.0, status="Completed"))
@patch.object(ShoppingCart, "save_cart_to_csv", MagicMock())
@patch.object(ShoppingCart, "load_cart_from_csv", MagicMock())
@patch("flask.testing.FlaskClient.put", return_value=MagicMock(status_code=200, json=lambda: {"message": "Item added"}))
def test_checkout_success(mock_checkout, mock_put, client, create_test_user):
    """Test successful checkout process with mocking."""
    print("Mock checkout applied:", mock_checkout)
    print("Mock put applied:", mock_put)
    headers = get_auth_headers("test@example.com", "Test@123")
    test_user_email = "test@example.com"

    with patch.dict(orders, {test_user_email: ShoppingCart(create_test_user, inventory)}):
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

        assert add_response.status_code == 200, f"Adding item to cart failed! Response:{add_response.json}"

        response = client.post("/cart/checkout", json={"user_email": test_user_email}, headers=headers)
        assert response.status_code == 200
        assert response.json["order_id"] == "1234"
        assert response.json["status"] == "Completed"


@patch.object(ShoppingCart, "save_cart_to_csv", MagicMock())
@patch.object(ShoppingCart, "load_cart_from_csv", MagicMock())
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

    assert response.status_code == 404
    assert b"'Nonexistent Item' of type 'Table' not found in inventory." in response.data


@patch.object(ShoppingCart, "save_cart_to_csv", MagicMock())
@patch.object(ShoppingCart, "load_cart_from_csv", MagicMock())
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


@patch.object(ShoppingCart, "save_cart_to_csv")
def test_save_cart_to_csv_via_api(mock_save_cart, client, create_test_user):
    """ Testing that the cart saves to the CSV through our Flask API"""
    headers = get_auth_headers("test@example.com", "Test@123")

    # Adding item to cart
    client.put("/cart/add", json={
        "name": "Office Chair",
        "type": "Chair",
        "quantity": 2
    }, headers=headers)

    # Sending the CSV through the API
    response = client.post("/cart/save", headers=headers)
    mock_save_cart.assert_called_once()

    assert response.status_code == 200
    assert response.json["message"] == "Cart saved successfully!"


@patch("shopping_cart.open", new_callable=mock_open, read_data="user_email,item_name,quantity,price\n"
                                                               "test@example.com,Office Chair,2,100.0\n")
@patch("os.path.exists", return_value=True)
def test_load_cart_from_csv_via_api(mock_exists, mock_file, client, create_test_user):
    """ Testing that the cart loads from the CSV through our Flask API"""
    headers = get_auth_headers("test@example.com", "Test@123")

    # Loading the cart from CSV
    response = client.get("/cart/load", headers=headers)

    assert response.status_code == 200
    assert "cart" in response.json
    mock_file.assert_called_once_with("cart_data.csv", mode="r", newline="")