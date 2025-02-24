from flask import Flask, request, jsonify
from flask_httpauth import HTTPBasicAuth
from User import User
from shopping_cart import ShoppingCart
from inventory import Inventory


app = Flask(__name__)
auth = HTTPBasicAuth()
# Initialize inventory and users
inventory = Inventory()
users = {}
orders = {}


@auth.verify_password
def verify_password(email, password):
    user = users.get(email)
    if user and user.check_password(password):
        return user
    return None


@app.route("/")
def home():
    return "Welcome to the Online Furniture Store API!"


@app.route("/user/register", methods=["POST"])  # User Registration
def register_user():
    data = request.json
    email = data["email"]
    if email in users:
        return jsonify({'error': 'User already exists'}), 400

    new_user = User(
        name=data["name"],
        email=data["email"],
        password=data["password"],
        address=data["address"],
        payment_method=data.get("payment_method", "Credit Card")
    )
    users[email] = new_user
    return jsonify({'message': 'User registered successfully'}), 201


@app.route("/user/login", methods=["POST"])  # User login
def login_user():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    user = users.get(email)
    if not user:
        return jsonify({"error": "User email not found."}), 404

    if not user.check_password(password):
        return jsonify({"message": "Invalid password"}), 401

    return jsonify({
        "message": "Login Successful!", "user": {
            "name": user.name,
            "email": user.email,
            "address": user.address,
            "payment_method": user.payment_method,
            "order_history": user.view_order_history(),
        }})


@app.route("/furniture", methods=["GET"])  # Show all the furniture currently existent in inventory
def get_furniture():
    furniture_list = inventory.get_all_items()
    return jsonify(furniture_list)


# Add item to shopping cart
@app.route("/cart/add", methods=["POST"])
@auth.login_required
def add_to_cart():
    user = auth.current_user()
    data = request.json

    item_name = data.get("name")
    furniture_type = data.get("type")
    quantity = int(data.get("quantity", 1))

    item = inventory.items_by_type.get(furniture_type, {}).get(item_name)
    if not item:
        return jsonify({"error": f"Item '{item_name}' of type '{furniture_type}' not found in inventory."}), 404

    if item.available_quantity < quantity:
        return jsonify({"error": f"Not enough stock for {item_name}. Only {item.available_quantity} left."}), 400

    if user.email not in orders:
        orders[user.email] = ShoppingCart(user, inventory)

    cart = orders[user.email]
    cart.add_item(item, quantity)

    return jsonify({'message': f"{quantity} x {item_name} added to cart."}), 200


@app.route("/cart/view", methods=["GET"])  # View the user's shopping cart
@auth.login_required
def view_cart():
    user = auth.current_user()
    cart = orders.get(user.email)
    if not cart:
        return jsonify({"cart": "Your shopping cart is empty."})

    return jsonify(cart.view_cart())


@app.route("/cart/remove", methods=["POST"])  # Remove item from cart
@auth.login_required
def remove_item_from_cart():
    user = auth.current_user()
    data = request.json
    item_name = data.get("name")

    cart = orders.get(user.email)
    if not cart:
        return jsonify({"error": "No cart found for user."}), 404

    cart.remove_item(item_name)
    return jsonify({"message": f"{item_name} removed from cart."}), 200


@app.route('/cart/checkout', methods=['POST'])  # Checkout an order
@auth.login_required
def checkout():
    user = auth.current_user()
    cart = orders.get(user.email)
    if not cart or not cart.cart_items:
        return jsonify({"error": "Cart is empty"}), 400

    print("\n🔹 Starting checkout process...")
    print(f"🔹 Shipping to: {user.address}")
    print(f"🔹 Payment method: {user.payment_method}")

    order = cart.checkout()  # Using The Checkout method from Shopping_cart.py

    if not order:
        return jsonify({"error": "Checkout failed. Please check stock availability or payment method."}), 400

    return jsonify({
        "message": "Order placed successfully!",
        "order_id": order.order_id,
        "total_price": order.total_price,
        "status": order.status,
        "payment_method": user.payment_method,
        "items": [{"name": item.name, "quantity": quantity} for item, quantity in order.items.items()]

    })


if __name__ == '__main__':
    app.run(debug=True)
