import datetime
import jwt
import json
import atexit
import os
from functools import wraps
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_httpauth import HTTPTokenAuth
from User import User
from shopping_cart import ShoppingCart
from inventory import Inventory
from furniture import FurnitureFactory


# General definitions related to the API
app = Flask(__name__)
SECRET_KEY = "your_secret_key"
auth = HTTPTokenAuth(scheme="Bearer")  # Will be used as the authentication decorator "@auth" for
# actions that require login

# File Paths for data (by JSON)
USERS_FILE = "data/users.json"
ORDERS_FILE = "data/orders.json"
CARTS_FILE = "data/shopping_carts.json"
inventory = Inventory()  # Assume Inventory is initialized from a file or database

if not os.path.exists("data"):
    os.makedirs("data")

if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w") as f:
        json.dump({}, f)

# ===========================
# Methods and actions for defining the authorization
# ===========================

# A Dictionary identifying if a user is an admin or regular client
admins = {"admin@example.com": True}


# Generate JWT Token
def generate_token(user):
    """Generate JWT token with user role information."""
    payload = {
        'email': user.email,
        'exp': datetime.utcnow() + timedelta(days=1),
        'admin': getattr(user, 'is_admin', False)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token


# Authenticate user setup
@auth.verify_token
def verify_token(token):
    """The function that is defined as the mechanism for verification"""
    try:
        user_info = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_email = user_info.get("email")
        print(f"Verifying user: {user_email}, Users in system: {list(users.keys())}")  # Debugging
        if user_email not in users:
            return None
        return user_email
    except jwt.ExpiredSignatureError:
        print("Token expired!")
        return None
    except jwt.InvalidTokenError:
        print("Invalid Token!")
        return None


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"error": "Missing token"}), 401
        user_email = verify_token(token.replace("Bearer ", ""))
        if not user_email or user_email != "admin@example.com":
            return jsonify({"error": "Unauthorized access"}), 403
        return f(*args, **kwargs)
    return decorated_function


# Function to check if a user has admin status
@auth.verify_token
def is_admin(email):
    """Check if the given user email belongs to an admin."""
    return admins.get(email, False)


def get_jwt_token(user):
    """Generate JWT token for test user"""
    payload = {
        'email': user.email,
        'exp': datetime.utcnow() + timedelta(hours=1),
        'role': users_roles.get(user.email, "client")
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    print(f"Generated Token: {token}")
    return token


# ===========================
# Helper methods to save and load data using JSON
# ===========================
def load_users_json():
    global users_roles

    try:
        with open(USERS_FILE, "r") as file:
            users_data = json.load(file)
            users_dict = {}
            users_roles = {}
            for email, data in users_data.items():
                users_dict[email] = User(
                    name=data["name"],
                    email=data["email"],
                    password=data["password"],
                    address=data["address"],
                    payment_method=data.get("payment_method", "Credit Card"),
                )
                users_roles[email] = data.get("role", "client")

            return users_dict, users_roles
    except (FileNotFoundError, json.JSONDecodeError):
        return {}, {}


def load_orders_json():
    """Load orders from JSON file"""
    try:
        with open(ORDERS_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def load_carts_json():
    """Load shopping carts from JSON file"""
    global shopping_carts

    try:
        with open(CARTS_FILE, "r") as file:
            carts_data = json.load(file)

            shopping_carts = {}
            for email, cart_data in carts_data.items():
                if email in users:
                    shopping_carts[email] = ShoppingCart(users[email], inventory)
                else:
                    print(f"⚠️ Warning: User {email} not found in users. Skipping cart load.")
        return shopping_carts
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_users_json():
    """Save users to JSON file, including their roles"""
    users_data = {
        email: {
            "name": user.name,
            "email": user.email,
            "password": user.password,
            "address": user.address,
            "payment_method": user.payment_method,
            "role": users_roles.get(email, "client")
        }
        for email, user in users.items() if isinstance(user, User)
    }

    with open(USERS_FILE, "w") as file:
        json.dump(users_data, file, indent=4)


def save_orders_json():
    """Save orders to JSON file"""
    with open(ORDERS_FILE, "w") as file:
        json.dump(orders, file, indent=4)


def save_carts_json():
    """Save shopping carts to JSON file"""
    carts_data = {
        email: {
            "items": [
                {"name": item.name, "type": item.__class__.__name__, "quantity": quantity}
                for item, quantity in cart.cart_items.items()
            ]
        }
        for email, cart in shopping_carts.items()
    }

    with open(CARTS_FILE, "w") as file:
        json.dump(carts_data, file, indent=4)


# Initialize the databases of inventory,users,orders and carts
users, users_roles = load_users_json()
orders = load_orders_json() or {}
shopping_carts = load_carts_json() or {}

# ===========================
# Methods and actions available for all users
# ===========================


@app.route("/")  # The default here is using the GET method
def home():
    return jsonify({
        "message": "Welcome to the Online Furniture Store API!",
        "endpoints": {
            "public": ["/user/register", "/user/login", "/furniture", "/furniture/search"],
            "customer": ["/cart/view", "/cart/update", "/cart/remove", "/cart/checkout"],
            "admin": ["/admin/inventory/manage", "/admin/orders", "/admin/manage_users"]
        }
    })


@app.route("/register", methods=["POST"])  # User Registration
def register_user():
    """Register a new user to the system"""
    data = request.json
    if not data or not all(k in data for k in ["name", "email", "password", "address"]):
        return jsonify({"error": "Missing required fields"}), 400

    email = data["email"]  # Because we defined users to be recognized by their email address
    if email in users:
        return jsonify({'error': 'User already exists'}), 400

    new_user = User(
        name=data["name"],
        email=email,
        password=data["password"],
        address=data["address"],
        payment_method=data.get("payment_method", "Credit Card")
    )

    users[email] = new_user  # Save the new user that was registered
    return jsonify({'message': f"'User {data['name']} registered successfully"}), 201


@app.route("/login", methods=["POST"])  # User login
def login_user():
    """The user logs into the system with his details and gets Token"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Missing request body"}), 400

        email = data.get("email")
        password = data.get("password")
        if not email or not password:
            return jsonify({"error": "Missing email or password"}), 400

        user_data = users.get(email)
        if not user_data:
            print("User not found")
            return jsonify({"error": "User not found"}), 404
        if isinstance(user_data, dict):
            user_obj = User(
                name=user_data["name"],
                email=user_data["email"],
                password=user_data["password"],
                address=user_data["address"],
                payment_method=user_data["payment_method"]
            )
        else:
            user_obj = user_data

        if user_obj.check_password(password):
            print("Password incorrect")
            token = generate_token(user_obj)
            return jsonify({
                "message": "Login Successful!",
                "token": token,
                "role": users_roles.get(email, "client")
            }), 200

        return jsonify({"error": "Invalid email or password"}), 401
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401
    except Exception as e:
        print(f"Login Error: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500


# ========= Client Endpoints ========= #
@app.route("/furniture", methods=["GET"])  # Show all the furniture currently existent in inventory
def get_furniture():
    """To view all available furniture in the store"""
    try:
        furniture_catalog = inventory.get_all_items()
        return jsonify(furniture_catalog), 200
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred while retrieving the furniture.",
                        "details": str(e)}), 500


@app.route("/furniture/search", methods=["GET"])
def search_furniture():
    """Search for a furniture item by name and type"""
    name = request.args.get("name")
    furniture_type = request.args.get("type")
    if not name or not furniture_type:
        return jsonify({"error": "Both 'name' and 'type' parameters are required"}), 400

    search_results = inventory.search(name=name, type=furniture_type)
    if not search_results:
        return jsonify({"error": f"Item '{name}' of type '{furniture_type}' not found in inventory."}), 404

    return jsonify([{
        "id": item.u_id,
        "name": item.name,
        "type": item.type,
        "price": item.price,
        "available_quantity": item.available_quantity
    }
        for item in search_results]), 200


@app.route("/cart/view", methods=["GET"])  # View the user's shopping cart
@auth.verify_token  # We restricted this action to be available only to users that are logged in
def view_cart():
    """View all the items that composite the user's cart"""
    user_email = request.args.get("user_email")
    if not user_email:
        return jsonify({"error": "User email is required"}), 400

    user = users.get(user_email)
    if not user:
        return jsonify({"error": "User not found"}), 404

    if user_email not in shopping_carts:
        shopping_carts[user_email] = ShoppingCart(user, inventory)

    cart = shopping_carts[user_email]
    if not cart:
        return jsonify({"cart": "Your shopping cart is empty."})
    return jsonify(cart.view_cart()), 200


# Add item to shopping cart
@app.route("/cart/add", methods=["PUT"])
@auth.verify_token  # We restricted this action to be available only to users that are logged in
def add_to_cart():
    """Adding an item to the cart"""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid request, missing JSON data"}), 400
    print("Headers received:", request.headers)  # Debugging
    print(f"Request received: {data}")

    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    print(f"Received token: {token}")

    user = auth.current_user()
    print(f"Authenticated user: {user.email if user else 'No user'}")
    if not user:
        return jsonify({"error": "User authentication failed."}), 401

    user_email = user.email
    if user_email not in users:
        print(f"User {user_email} not found in system!")
        return jsonify({"error": "User authentication failed."}), 401

    users_roles[user_email] = "client"

    item_name = data.get("name")
    furniture_type = data.get("type")
    quantity = int(data.get("quantity", 1))

    if not item_name or not furniture_type:
        return jsonify({"error": "Missing required fields"}), 400

    if user_email not in shopping_carts:
        shopping_carts[user_email] = ShoppingCart(user, inventory)

    cart = shopping_carts[user_email]   # Extract the user's cart
    search_results = inventory.search(name=item_name, type=furniture_type)   # Search the desired item

    if not search_results:
        print(f"Item '{item_name}' of type '{furniture_type}' not found in inventory.")
        return jsonify({"error": f"Item '{item_name}' of type '{furniture_type}' not found in inventory."}), 404
    item = search_results[0]
    if item.available_quantity < quantity:
        print(f"Not enough stock for {item_name}. Only {item.available_quantity} left.")
        return jsonify({"error": f"Not enough stock for {item_name}. Only {item.available_quantity} left."}), 400

    cart.add_item(item, quantity)
    print(f"{quantity} x {item_name} added to cart successfully!")
    return jsonify({'message': f"{quantity} x {item_name} added to cart."}), 200


@app.route("/cart/remove", methods=["DELETE"])  # Remove item from cart
@auth.verify_token
def remove_item_from_cart():  # We restricted this action to be available only to users that are logged in
    """Remove an item from the cart"""
    print("Headers received:", request.headers)

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid request, missing JSON data"}), 400
    print(f"Received data for removal: {data}")

    user_email = data.get("user_email")
    item_name = data.get("name")
    item_type = data.get("type")
    quantity = data.get("quantity")

    if not all([user_email, item_name, item_type, quantity]):
        return jsonify({"error": "Missing required fields"}), 400

    if user_email not in users or user_email not in shopping_carts:
        return jsonify({"error": "User not found or cart does not exist"}), 404

    found_items = inventory.search(name=item_name, type=item_type)
    if not found_items:
        return jsonify({"error": f"Item {item_name} not found in inventory"}), 404
    found_item = found_items[0]
    user_cart = shopping_carts[user_email]
    if not user_cart:
        return jsonify({"error": "Cart not found"}), 404
    if found_item not in user_cart.cart_items:
        return jsonify({"error": f"Item {item_name} not found in cart"}), 404

    user_cart.remove_item(found_item, quantity)
    if found_item in user_cart.cart_items:
        return jsonify({"error": f"Failed to remove item {item_name} from cart"}), 404

    return jsonify({"message": f"Removed {quantity} of {item_name} from cart"}), 200


@app.route('/cart/checkout', methods=['POST'])  # Checkout an order
@auth.verify_token  # We restricted this action to be available only to users that are logged in
def checkout():
    user_email = request.json.get("user_email")
    user = users.get(user_email)
    if not user:
        print(" User not found in users database!")
        return jsonify({"error": "User not found"}), 400

    if not user_email or user_email not in shopping_carts:
        print(f" Cart not found for user: {user_email}")
        return jsonify({"error": "Cart is empty"}), 400

    shopping_carts[user_email].save_cart_to_csv()
    user_cart = shopping_carts.get(user_email)
    order = user_cart.checkout()  # Using The Checkout method from Shopping_cart.py

    if not order:
        print(" Checkout failed! Possible stock/payment issue.")
        return jsonify({"error": "Checkout failed. Please check stock availability or payment method."}), 400

    return jsonify({
        "message": "Order placed successfully!",
        "order_id": order.order_id,
        "total_price": order.total_price,
        "status": order.status,
        "payment_method": user.payment_method,
        "items": [{"name": item.name, "quantity": quantity} for item, quantity in order.items.items()]
    }), 200


@app.route('/cart/save', methods=['POST'])
@auth.verify_token
def save_cart_to_csv():  # We restricted this action to be available only to users that are logged in
    """Save the shopping cart to CSV"""
    print("Headers received:", request.headers)  # Debugging
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    print(f"Received token: {token}")

    user = auth.current_user()
    print(f"Authenticated user: {user.email if user else 'No user'}")  # Debugging
    if not user:
        return jsonify({"error": "User authentication failed."}), 401

    user_email = user.email
    print("Users in system before saving cart:", users.keys())

    if user_email not in shopping_carts:
        return jsonify({"error": "Cart not found for user"}), 404

    print(f"Saving cart for user: {user_email}")
    shopping_carts[user_email].save_cart_to_csv()
    return jsonify({"message": "Cart saved successfully!"}), 200


@app.route('/cart/load', methods=['GET'])
@auth.verify_token
def load_cart_from_csv():  # We restricted this action to be available only to users that are logged in
    """Load the user's shopping cart from CSV"""
    print("Headers received:", request.headers)  # Debugging
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    print(f"Received token: {token}")

    user = auth.current_user()
    print(f"Authenticated user: {user.email if user else 'No user'}")  # Debugging
    if not user:
        return jsonify({"error": "User authentication failed."}), 401

    user_email = user.email
    if user_email not in shopping_carts:
        # If there's no existent cart, create a new one
        shopping_carts[user_email] = ShoppingCart(user.email, inventory)

    cart = shopping_carts[user_email]
    cart.load_cart_from_csv()
    return jsonify({"message": "Cart Loaded Successfully!",
                    "cart": {item.name: quantity for item, quantity in cart.cart_items.items()}
                    }), 200


@app.route("/admin/inventory/manage", methods=["POST", "PUT", "DELETE", "GET"])
@auth.verify_token
@admin_required
def manage_inventory():
    """Manage inventory - Add,Update or Delete items"""
    user_email = request.json.get('email')
    if not is_admin(user_email):
        return jsonify({"error": "Unauthorized access"}), 403

    data = request.json
    # GET - Retrieve inventory items
    if request.method == "GET":
        return jsonify(inventory.get_all_items()), 200
    # Extract common fields
    item_name = data.get("name")
    furniture_type = data.get("type")

    if not item_name or not furniture_type:
        return jsonify({"error": "Missing required fields(name, type)."}), 400

    # POST - Add new item
    if request.method == "POST":
        try:
            new_item = FurnitureFactory.create_furniture(**data)
            inventory.add_item(new_item)

            inventory.notify_observers(new_item, "added")
            return jsonify({"message": f"Item '{new_item.name}' added successfully"}), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    # PUT - Update item quantity
    elif request.method == "PUT":
        new_quantity = data.get("quantity")
        if new_quantity is None:
            return jsonify({"error": "Missing 'quantity' field."}), 400

        items = inventory.search(name=item_name, furniture_type=furniture_type)
        if not items:
            return jsonify({"error": f"Item '{item_name}' not found in inventory."}), 404

        # Search for the item
        item = items[0]
        try:
            inventory.update_quantity(item, furniture_type, new_quantity)
            inventory.notify_observers(item, "updated")
            return jsonify({"message": f"Updated '{item_name}' quantity to {new_quantity}."}), 200

        except ValueError as e:
            return jsonify({"error": str(e)}), 400

    # DELETE - Remove an item from inventory
    elif request.method == "DELETE":
        items = inventory.search(name=item_name, furniture_type=furniture_type)
        if not items:
            return jsonify({"error": f"Item '{item_name}' not found in inventory."}), 404

        item = items[0]
        inventory.remove_item(item, furniture_type=furniture_type)
        inventory.notify_observers(item, "deleted")
        return jsonify({"message": f"Item '{item_name}' removed successfully"}), 200

    return jsonify({"error": "Invalid request method."}), 405


@app.route("/admin/orders", methods=["GET"])
@auth.verify_token
@admin_required
def view_orders():
    """View all customer orders"""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not token:
        return jsonify({"error": "Missing token"}), 401
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        print("Decoded JWT:", payload)

    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401
    user_email = payload.get("email")
    user_role = payload.get("role")

    if user_role != "admin":
        print(f" Unauthorized access attempt by {user_email}")
        return jsonify({"error": "Unauthorized access"}), 403
    if not orders:
        print(" No orders found")
        return jsonify({"message": "No orders found"}), 404

    print("🟢 Returning orders data")
    return jsonify({"orders": list(orders.values())}), 200


@app.route("/admin/manage_users", methods=["GET", "PUT", "DELETE"])
@auth.verify_token
@admin_required
def manage_users():
    """Manage users - View, Update, or Delete"""
    print("Headers received:", request.headers)  # Debugging
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    print(f"Received token: {token}")

    user = auth.current_user()
    print(f"Authenticated user: {user.email if user else 'No user'}")  # Debugging
    if not user or not is_admin(user.email):
        print("Unauthorized access attempt")
        return jsonify({"error": "Unauthorized access"}), 403

    # GET - Return all users
    if request.method == "GET":
        users_list = {
            email: {
                "name": u.name,
                "email": u.email,
                "role": users_roles.get(email, "client")
            }
            for email, u in users.items() if isinstance(u, User)
        }
        return jsonify({"users": users_list}), 200

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid request, missing JSON data"}), 400

    email = data.get("email")
    if not email or email not in users:
        return jsonify({"error": "User not found"}), 404

    user_obj = users[email]

    if request.method == "PUT":
        # Updating all the observers about details' updates
        updated_fields = {key: value for key, value in data.items() if key in ["name", "address", "payment_method"]}
        if not updated_fields and "role" not in data:
            return jsonify({"error": "No fields provided for update"}), 400

        for key, value in updated_fields.items():
            setattr(user_obj, key, value)

        if "role" in data and data["role"] in ["admin", "client"]:
            users_roles[email] = data["role"]

        # Alert all observers about updates
        if hasattr(user_obj, "notify_observers"):
            user_obj.notify_observers("profile_updated")

        save_users_json()
        return jsonify({"message": f"User {email} updated successfully."}), 200

    # DELETE - Remove a user
    elif request.method == "DELETE":
        # Send an alert to observers when deleting user
        if hasattr(user_obj, "notify_observers"):
            user_obj.notify_observers("user_deleted")
        del users[email]
        users_roles.pop(email, None)
        save_users_json()
        return jsonify({"message": f"User {email} deleted successfully."}), 200

    return jsonify({"error": "Invalid request method"}), 405


def save_all_data():
    """Before closing the API, saving all data to JSON files."""
    save_users_json()
    save_orders_json()
    save_carts_json()


atexit.register(save_all_data)


if __name__ == '__main__':
    app.run(debug=True)
