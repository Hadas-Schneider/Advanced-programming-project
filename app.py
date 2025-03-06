from flask import Flask, request, jsonify
from flask_httpauth import HTTPBasicAuth
from User import User
from shopping_cart import ShoppingCart
from inventory import Inventory


app = Flask(__name__)
auth = HTTPBasicAuth()  # Will be used as the basic authentication decorator "@auth" for actions that require login

# Initialize inventory,users and orders
inventory = Inventory()
users = {}
orders = {}


@auth.verify_password
def verify_password(email, password):  # The function that is defined as the mechanism for verification
    user = users.get(email)  # Get the user object that has the given email address in the Users' database
    if user and user.check_password(password):  # If there is such user and his password fits the criteria
        return user
    return None


@app.route("/")  # The default here is using the GET method
def home():
    return jsonify({  # Show the main endpoints of the application and how the home page should look like
        "message": "Welcome to the Online Furniture Store API!",
        "endpoints": [
            "/user/register",
            "/user/login",
            "/cart/view",
            "/cart/update",
            "/cart/remove",
            "/cart/checkout",
            "/furniture"
        ]
    })


@app.route("/user/register", methods=["POST"])  # User Registration
def register_user():
    """Register a new user to the system"""
    data = request.json
    email = data["email"]  # Because we defined users to be recognized by their email address
    if email in users:
        return jsonify({'error': 'User already exists'}), 400

    new_user = User(
        name=data["name"],
        email=data["email"],
        password=data["password"],
        address=data["address"],
        payment_method=data.get("payment_method", "Credit Card")
    )
    users[email] = new_user  # Save the new user that was registered
    return jsonify({'message': 'User registered successfully'}), 201


@app.route("/user/login", methods=["POST"])  # User login
def login_user():
    """The user logs into the system with his details"""
    data = request.json
    email = data.get("email")
    user = users.get(email)
    password = data.get("password")
    if not user:  # If the user's not saved in the user's database return that he was not found
        return jsonify({"error": "User email not found."}), 404

    if not user.check_password(password):  # If the user's password doesn't meet the criteria
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
def get_furniture():  # To observe all the inventory that exists in the store
    furniture_list = inventory.get_all_items()
    return jsonify(furniture_list)


# Add item to shopping cart
@app.route("/cart/add", methods=["PUT"])
@auth.login_required  # We restricted this action to be available only to users that are logged in
def add_to_cart():
    """Adding an item to the cart"""
    user = auth.current_user()
    data = request.json

    item_name = data.get("name")
    furniture_type = data.get("type")
    quantity = int(data.get("quantity", 1))

    if user.email not in orders:  # Create a new cart for user if he doesn't have one in the Orders' database
        orders[user.email] = ShoppingCart(user, inventory)

    cart = orders[user.email]  # Extract the user's cart from the Orders' database

    item = inventory.items_by_type.get(furniture_type, {}).get(item_name)
    if not item:
        return jsonify({"error": f"Item '{item_name}' of type '{furniture_type}' not found in inventory."}), 404

    if item.available_quantity < quantity:
        return jsonify({"error": f"Not enough stock for {item_name}. Only {item.available_quantity} left."}), 400

    cart.add_item(item, quantity)
    return jsonify({'message': f"{quantity} x {item_name} added to cart."}), 200


@app.route("/cart/view", methods=["GET"])  # View the user's shopping cart
@auth.login_required  # We restricted this action to be available only to users that are logged in
def view_cart():
    user = auth.current_user()
    cart = orders.get(user.email)
    if not cart:
        return jsonify({"cart": "Your shopping cart is empty."})

    return jsonify(cart.view_cart())


@app.route("/cart/remove", methods=["DELETE"])  # Remove item from cart
@auth.login_required
def remove_item_from_cart():  # We restricted this action to be available only to users that are logged in
    """Remove an item from the cart"""
    user = auth.current_user()
    data = request.json

    if "item_name" not in data or not data["item_name"]:  # If there's no item_name in the data or in cart
        return jsonify({"error": "Item name is missing in request."}), 400

    item_name = data["item_name"]

    if user.email not in orders or not orders[user.email].cart_items:
        return jsonify({"error": "No cart found for user."}), 404

    # Prepare the cart
    cart = orders[user.email]
    # Get all items of the cart
    item = next((i for i in cart.cart_items.keys() if i.name == item_name), None)
    if not item:
        return jsonify({"error": f"Item '{item_name}' is not in the cart."}), 404

    cart.remove_item(item)  # Call for the remove_item method from Shopping_cart.py
    return jsonify({"message": f"Removed {item_name} from cart."}), 200


@app.route('/cart/checkout', methods=['POST'])  # Checkout an order
@auth.login_required  # We restricted this action to be available only to users that are logged in
def checkout():
    user = auth.current_user()
    if user.email not in orders:
        return jsonify({"error": "Cart is empty"}), 400

    cart = orders[user.email]

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
    }), 200


@app.route('/cart/save', methods=['POST'])
@auth.login_required()
def save_cart_to_csv():  # We restricted this action to be available only to users that are logged in
    """Save the shopping cart to CSV"""
    user = auth.current_user()
    if user.email not in orders:
        return jsonify({"error": "No cart found for user."}), 404
    cart = orders[user.email]
    cart.save_cart_to_csv()
    return jsonify({"message": "Cart saved successfully!"}), 200


@app.route('/cart/load', methods=['GET'])
@auth.login_required
def load_cart_from_csv():  # We restricted this action to be available only to users that are logged in
    """Load the user's shopping cart from CSV"""
    user = auth.current_user()

    if user.email not in orders:  # If there's no existent cart, create a new one
        orders[user.email] = ShoppingCart(user, inventory)

    cart = orders[user.email]
    cart.load_cart_from_csv()
    return jsonify({"message": "Cart Loaded Successfully!",
                    "cart": {item.name: quantity for item, quantity in cart.cart_items.items()}
                    }), 200


if __name__ == '__main__':
    app.run(debug=True)
