from flask import Flask, request, jsonify
import csv
from inventory import Inventory
from User import User
from shopping_cart import ShoppingCart
from furniture import FurnitureFactory
from order import Order
import pandas as pd


app = Flask(__name__)

# Initialize inventory and users
inventory = Inventory()
users = {}

# df = pd.read_csv("furniture_database.csv")
# print(df[['u_id','Type']])


def load_furniture_data():
    global inventory
    with open("furniture_database.csv", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                # Determine the type of furniture and instantiate the corresponding class
                item = FurnitureFactory.create_furniture(
                    row["Type"],
                    u_id = row["u_id"],
                    name = row["Name"],
                    description = row["Description"],
                    material = row["Material"],
                    color = row["Material"],
                    wp = int(row["Warranty Period"]),
                    price = float(row["Price (in US Dollars"]),
                    dimensions = tuple(map(int, row["Dimensions"].split("x"))),
                    country = row["Country of Creation"],
                    available_quantity = int(row.get("Available Quantity", 0)),
                )
                inventory.add_item(item)
            except Exception as e:
                print(f"Error processing row {row}: {e}")


load_furniture_data()
# print(inventory.view_inventory())


@app.route("/")
def home():
    return "Welcome to the Online Furniture Store API!"


# User registration
@app.route("/user/register", methods=["POST"])
def register_user():
    data = request.json
    if data["email"] in users:
        return jsonify({"error": "User already exists"}), 400

    users[data["email"]] = User(
    data["name"], data["email"], data["password"], data["address"]
    )
    return jsonify({"message": "User registered successfully"})


# User login (simple check)
@app.route("/user/login", methods=["POST"])
def login_user():
    data = request.json
    user = users.get(data["email"])
    if not user or not user.check_password(data["password"]):
        return jsonify({"error": "Invalid email or password"}), 401

    return jsonify({"message": "Login successful"})


# Get all furniture items
# @app.route('/furniture', methods=['GET'])
# def get_furniture():
#     inventory1 = load_furniture_data()
#     furniture_items = inventory1.get_all_items()
#     return jsonify(furniture_items), 200

@app.route("/furniture", methods=["GET"])
def get_furniture():
    inventory = load_furniture_data()
    furniture_list = []
    for furniture_type, items in inventory.items_by_type.items():
        for item in items.values():
            furniture_list.append({
                "u_id": item.u_id,
                "Type": furniture_type,
                "Name": item.name,
                "Price": item.price,
                "Available Quantity": item.available_quantity
            })
    return jsonify(furniture_list)

# Get a single furniture item by ID
@app.route("/furniture/<u_id>", methods=["GET"])
def get_furniture_item(u_id):
    for type_items in inventory.items_by_type.values():
        for item in type_items.values():
            if item.u_id == u_id:
                return jsonify({
                    "id": item.u_id,
                    "name": item.name,
                    "price": item.price,
                    "available_quantity": item.available_quantity
                })
    return jsonify({"error": "Item not found"}), 404


# Add item to shopping cart
@app.route("/cart", methods=["POST"])
def add_to_cart():
    data = request.json
    user = users.get(data["email"])
    if not user:
        return jsonify({"error": "User not found"}), 404

    cart = ShoppingCart(user)
    for item_data in data["items"]:
        item = inventory.search(name=item_data["name"])
        if item:
            cart.add_item(item[0], item_data["quantity"])

    return jsonify({"message": "Items added to cart"})


# Checkout
@app.route("/checkout", methods=["POST"])
def checkout():
    data = request.json
    user = users.get(data["email"])
    if not user:
        return jsonify({"error": "User not found"}), 404

    cart = ShoppingCart(user)
    order = cart.checkout(inventory)
    if order:
        return jsonify({"message": "Order placed successfully", "order_id": order.order_id})
    return jsonify({"error": "Checkout failed"}), 400


if __name__ == "__main__":
    app.run(debug=True)