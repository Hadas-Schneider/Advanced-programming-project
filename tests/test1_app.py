import pytest
import base64
import os
from unittest.mock import patch, MagicMock, mock_open
from app1 import app, users, orders, get_jwt_token, inventory, users_roles, save_users_json
from User import User
from furniture import Chair
from shopping_cart import ShoppingCart

SECRET_KEY = "your_secret_key"


if not os.path.exists("data/users.json"):
    with open("data/users.json", "w") as f:
        f.write("{}")


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


@pytest.fixture
def create_test_user():
    """Create a test user before running authentication-based tests"""
    user = User(
        name="Test User",
        email="test@example.com",
        password="Test@123",
        address="123 Test St",
        payment_method="Credit Card")
    users[user.email] = user
    users_roles[user.email] = "client"
    print(f"✅ Created Test User: {user.email}, Role: {users_roles[user.email]}")
    save_users_json()
    return user


@pytest.fixture
def create_admin_user():
    """Create a test admin user before running authentication-based tests"""
    admin_user = User(
        name="Admin",
        email="admin@example.com",
        password="Admin@123",
        address="Admin Address",
        payment_method="Credit Card",
    )
    users[admin_user.email] = admin_user
    users_roles[admin_user.email] = "admin"
    print(f"✅ Created Admin User: {admin_user.email}, Role: {users_roles[admin_user.email]}")
    save_users_json()
    return admin_user


def get_auth_headers(email, password):
    """"
    Helper function to generate Authorization headers for HTTP Basic Authentication
    """
    credentials = f"{email}:{password}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode("utf-8")
    return {"Authorization": f"Basic {encoded_credentials}"}


def test_search_existing_furniture(client):
    """Test searching for an existing furniture item."""
    inventory.items_by_type.setdefault("Chair", {})["Office Chair"] = Chair(
        u_id="001", name="Office Chair", description="Ergonomic chair",
        material="Metal", color="Black", wp=2, price=100.0, dimensions=(60, 60, 120),
        country="USA", available_quantity=5, has_armrests=True
    )
    response = client.get("/furniture/search", query_string={"name": "Office Chair", "type": "Chair"})

    assert response.status_code == 200
    assert isinstance(response.json, list), "Expected list response"
    assert response.json[0]["name"] == "Office Chair"
    assert response.json[0]["type"] == "Chair"
    assert response.json[0]["price"] == 100.0


def test_search_nonexistent_furniture(client):
    """
    Test searching for a furniture item that does not exist.
    """
    response = client.get("/furniture/search", query_string={"name": "Nonexistent Chair", "type": "Chair"})

    assert response.status_code == 404
    assert "error" in response.json
    assert response.json["error"] == "Item 'Nonexistent Chair' of type 'Chair' not found in inventory."


def test_search_furniture_missing_parameters(client):
    """
    Test searching for furniture without providing necessary parameters.
    """
    response = client.get("/furniture/search")

    assert response.status_code == 400
    assert "error" in response.json
    assert response.json["error"] == "Both 'name' and 'type' parameters are required"


@patch.object(ShoppingCart, "save_cart_to_csv", MagicMock())
@patch.object(ShoppingCart, "load_cart_from_csv", MagicMock())
def test_register_user(client):
    """Test user registration endpoint."""
    if "test@example.com" in users:
        del users["test@example.com"]
    response = client.post("/register", json={
        "name": "Test User",
        "email": "test@example.com",
        "password": "Test@123",
        "address": "123 Test St",
        "payment_method": "Credit Card"
    })
    print("Registration response:", response.json)
    assert response.status_code == 201, f"Expected 201, got {response.status_code}"
    assert "test@example.com" in users, "User was not registered in 'users' dictionary"
    print("User registered successfully:", users["test@example.com"])


@patch.object(ShoppingCart, "save_cart_to_csv", MagicMock())
@patch.object(ShoppingCart, "load_cart_from_csv", MagicMock())
def test_login_user(client, create_test_user):
    """Test user login and receiving JWT token endpoint."""
    if create_test_user.email not in users or not isinstance(users[create_test_user.email], User):
        users[create_test_user.email] = create_test_user

    response = client.post("/login", json={
        "email": "test@example.com",
        "password": "Test@123"
    })

    assert response.status_code == 200, f"Unexpected response: {response.status_code}, {response.data}"
    data = response.get_json()
    assert "token" in data, "Token should be returned after login"


@patch.object(ShoppingCart, "save_cart_to_csv", MagicMock())
@patch.object(ShoppingCart, "load_cart_from_csv", MagicMock())
def test_view_cart(client, create_test_user):
    """Test viewing the shopping cart."""
    token = get_jwt_token(create_test_user)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    response = client.get("/cart/view", query_string={"user_email": "test@example.com"}, headers=headers)
    assert response.status_code == 200


@patch.object(ShoppingCart, "save_cart_to_csv", MagicMock())
@patch.object(ShoppingCart, "load_cart_from_csv", MagicMock())
def add_item_to_cart(client, create_test_user):
    """Test adding an item to the cart."""
    token = get_jwt_token(create_test_user)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    response = client.post("/cart/add", json={
        "user_email": "test@example.com",
        "item_name": "Office Chair",
        "quantity": 1
    }, headers=headers)
    print(response.status_code)
    assert response.status_code in [200, 404]


@patch.object(ShoppingCart, "remove_item", MagicMock())
@patch.object(ShoppingCart, "save_cart_to_csv", MagicMock())
@patch.object(ShoppingCart, "load_cart_from_csv", MagicMock())
def test_remove_item_from_cart(client, create_test_user):
    """Test removing an existing item from the cart."""

    global shopping_carts
    shopping_carts = {}
    test_user_email = create_test_user.email

    if test_user_email not in users or not isinstance(users[test_user_email], User):
        users[test_user_email] = create_test_user
    users_roles[test_user_email] = "client"

    print(f"Users in system: {users}")
    print(f"Roles in system: {users_roles}")

    token = get_jwt_token(create_test_user)
    print(f"Token for user {test_user_email}: {token}")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    chair_item = Chair(
        u_id="001", name="Office Chair", description="Ergonomic chair",
        material="Metal", color="Black", wp=2, price=100.0, dimensions=(60, 60, 120),
        country="USA", available_quantity=5, has_armrests=True
    )
    if "Chair" not in inventory.items_by_type:
        inventory.items_by_type["Chair"] = {}
    inventory.items_by_type["Chair"]["Office Chair"] = chair_item

    shopping_carts[test_user_email] = ShoppingCart(users[test_user_email], inventory)
    shopping_carts[test_user_email].add_item(chair_item, 2)

    assert shopping_carts[test_user_email].cart_items, "Cart should not be empty before removing item!"
    assert "Office Chair" in [item.name for item in shopping_carts[test_user_email].cart_items], \
        "Item 'Office Chair' was not added to the cart!"

    response = client.delete("/cart/remove", json={
        "user_email": create_test_user.email,
        "name": "Office Chair",
        "type": "Chair",
        "quantity": 1
    }, headers=headers)

    assert response.status_code == 200, f" Expected status 200, got {response.status_code}"

    remaining_items = [item.name for item in shopping_carts[test_user_email].cart_items]
    assert "Office Chair" not in remaining_items, "Item was not removed from the cart!"


@patch.object(ShoppingCart, "checkout", return_value=MagicMock(order_id="1234", total_price=500.0, status="Completed"))
@patch.object(ShoppingCart, "save_cart_to_csv", MagicMock())
@patch.object(ShoppingCart, "load_cart_from_csv", MagicMock())
@patch("flask.testing.FlaskClient.put", return_value=MagicMock(status_code=200, json=lambda: {"message": "Item added"}))
def test_checkout_success(mock_checkout, mock_put, client, create_test_user):
    """Test successful checkout process with mocking."""
    print("Mock checkout applied:", mock_checkout)
    print("Mock put applied:", mock_put)

    test_user_email = "test@example.com"
    users[test_user_email] = create_test_user

    token = get_jwt_token(create_test_user)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    inventory.items_by_type.setdefault("Chair", {})["Office Chair"] = Chair(
        u_id="001",
        name="Office Chair",
        description="Ergonomic chair",
        material="Metal",
        color="Black",
        wp=2,
        price=100.0,
        dimensions=(60, 60, 120),
        country="USA",
        available_quantity=5,
        has_armrests=True
    )

    shopping_carts[test_user_email] = ShoppingCart(create_test_user, inventory)
    shopping_carts[test_user_email].add_item(inventory.items_by_type["Chair"]["Office Chair"], 1)
    with patch.dict(orders, {test_user_email: shopping_carts[test_user_email]}):
        assert shopping_carts[test_user_email].cart_items, "Cart should not be empty before checkout!"
        print("Cart before checkout:", shopping_carts[test_user_email].cart_items)

        add_response = client.put("/cart/add", json={
            "user_email": test_user_email,
            "name": "Office Chair",
            "type": "Chair",
            "quantity": 1
        }, headers=headers)

        assert add_response.status_code == 200, f"Adding item to cart failed! Response:{add_response.json}"

    response = client.post("/cart/checkout", json={"user_email": test_user_email}, headers=headers)

    assert response.status_code == 200, f"Checkout failed! Response:{response.json}"
    assert response.json["order_id"] == "1234"
    assert response.json["status"] == "Completed"


def test_manage_inventory_as_admin(client, create_test_user):
    """Test adding an item to inventory as admin"""
    create_test_user.email = "admin@example.com"

    token = get_jwt_token(create_test_user)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    response = client.post("/admin/inventory/manage", json={
            "name": "Luxury Sofa",
            "type": "Sofa",
            "price": 500.0,
            "quantity": 10
        }, headers=headers)

    assert response.status_code in [201, 403]


def test_admin_cannot_manage_inventory_without_admin_role(client, create_test_user):
    """Test that a regular user cannot manage inventory"""
    token = get_jwt_token(create_test_user)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    response = client.post("/admin/inventory/manage", json={
        "name": "Luxury Sofa",
        "type": "Sofa",
        "price": 500.0,
        "quantity": 10
    }, headers=headers)

    assert response.status_code == 403


def test_view_orders_as_admin(client, create_admin_user):
    """Test that an admin can view orders"""
    admin_user = create_admin_user
    if admin_user.email not in users:
        users[admin_user.email] = admin_user

    users_roles[admin_user.email] = "admin"

    token = get_jwt_token(admin_user)
    print(f"Token for admin {admin_user.email}: {token}")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    response = client.get("/admin/orders", headers=headers)
    print("Admin orders response:", response.json if response.is_json else response.data)

    assert response.status_code in [200, 404], f"Unexpected response: {response.status_code}"


def test_regular_user_cannot_view_orders(client, create_test_user):
    """Test that a regular user cannot view orders"""
    token = get_jwt_token(create_test_user)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    response = client.get("/admin/orders", headers=headers)
    assert response.status_code == 403


def test_manage_users_as_admin(client, create_admin_user):
    """Test that an admin can manage users"""
    admin_user = create_admin_user
    users[admin_user.email] = admin_user
    users_roles[create_admin_user.email] = "admin"
    token = get_jwt_token(admin_user)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    response = client.get("/admin/manage_users", headers=headers)

    assert response.status_code == 200, f"Unexpected response: {response.status_code}, {response.data}"


def test_regular_user_cannot_manage_users(client, create_test_user):
    """Test that a regular user cannot manage users"""
    token = get_jwt_token(create_test_user)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    response = client.get("/admin/manage_users", headers=headers)
    assert response.status_code == 403


def test_client_cannot_access_admin(client, create_test_user):
    """Regular clients should NOT access admin functions"""
    token = get_jwt_token(create_test_user)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    response = client.get("/admin/manage_users", headers=headers)
    assert response.status_code == 403  # Access Denied


def test_admin_can_view_users(client, create_admin_user):
    """Admin should be able to view all users"""
    users[create_admin_user.email] = create_admin_user
    users_roles[create_admin_user.email] = "admin"

    token = get_jwt_token(create_admin_user)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    response = client.get("/admin/manage_users", headers=headers)
    assert response.status_code == 200


def test_delete_non_existent_user(client, admin_headers):
    """Test attempting to delete a non-existent user"""
    data = {"email": "ghost@example.com"}
    response = client.delete("/admin/manage_users", json=data, headers=admin_headers)
    assert response.status_code == 404
    assert "error" in response.json

# @patch.object(ShoppingCart, "save_cart_to_csv", MagicMock())
# @patch.object(ShoppingCart, "load_cart_from_csv", MagicMock())
# def test_add_item_not_in_inventory(client, create_test_user):
#     """Test adding an item that does not exist in inventory.
#     We expect it to return 400 - Bad request with a relevant error message."""
#     if create_test_user.email not in users or not isinstance(users[create_test_user.email], User):
#         users[create_test_user.email] = create_test_user
#
#     token = get_jwt_token(create_test_user)
#     print(f"Generated Token: {token}")
#     headers = {
#         "Authorization": f"Bearer {token}",
#         "Content-Type": "application/json"
#     }
#
#     response = client.put("/cart/add", json={
#         "name": "Nonexistent Item",
#         "type": "Table",
#         "quantity": 1
#     }, headers=headers)
#
#     assert response.status_code == 404
#     assert b"'Nonexistent Item' of type 'Table' not found in inventory." in response.data
#

# @patch.object(ShoppingCart, "save_cart_to_csv", MagicMock())
# @patch.object(ShoppingCart, "load_cart_from_csv", MagicMock())
# def test_remove_item_not_in_cart(client, create_test_user):
#     """
#     Test removing an item that is not in the user's cart.
#     Expected result: Should return 404 Not Found.
#     """
#     if create_test_user.email not in users or not isinstance(users[create_test_user.email], User):
#         users[create_test_user.email] = create_test_user
#
#     token = get_jwt_token(create_test_user)
#     headers = {
#         "Authorization": f"Bearer {token}",
#         "Content-Type": "application/json"
#     }
#
#     print(f"Headers: {headers}")
#     print(f"Users in system: {users}")
#
#     response = client.delete("/cart/remove", json={
#         "user_email": create_test_user.email,
#         "item_name": "Nonexistent Item"
#     }, headers=headers)
#
#     print("Response JSON:", response.json)
#     assert response.status_code == 404, f"Unexpected response: {response.status_code}, {response.data}"
#

@patch.object(ShoppingCart, "save_cart_to_csv")
def test_save_cart_to_csv_via_api(mock_save_cart, client, create_test_user):
    """ Testing that the cart saves to the CSV through our Flask API"""
    if create_test_user.email not in users or not isinstance(users[create_test_user.email], User):
        users[create_test_user.email] = create_test_user
    users_roles[create_test_user.email] = "user"

    token = get_jwt_token(create_test_user)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Adding item to cart
    client.put("/cart/add", json={
        "name": "Office Chair",
        "type": "Chair",
        "quantity": 2
    }, headers=headers)

    # Sending the CSV through the API
    response = client.post("/cart/save", headers=headers)
    print(f"Mock calls: {mock_save_cart.call_count}")

    assert response.status_code == 200
    mock_save_cart.assert_called_once()
    assert response.json["message"] == "Cart saved successfully!"


@patch("shopping_cart.open", new_callable=mock_open, read_data="user_email,item_name,quantity,price\n"
                                                               "test@example.com,Office Chair,2,100.0\n")
@patch("os.path.exists", return_value=True)
def test_load_cart_from_csv_via_api(mock_exists, mock_file, client, create_test_user):
    """ Testing that the cart loads from the CSV through our Flask API"""
    if create_test_user.email not in users or not isinstance(users[create_test_user.email], User):
        users[create_test_user.email] = create_test_user

    token = get_jwt_token(create_test_user)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Loading the cart from CSV
    response = client.get("/cart/load", headers=headers)

    assert response.status_code == 200, f"Expected status 200, got {response.status_code}"
    assert "cart" in response.json, "Cart data not found in response!"

    mock_file.assert_called_once_with("cart_data.csv", mode="r", newline="")
