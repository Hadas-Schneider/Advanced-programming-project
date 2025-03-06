# Advanced Programming Project | Online Furniture Store 🛋️
-This Project was submitted by Rawad Safiya, Hadas Scheider , Tom Pashinsky and Dana Pugach-

Welcome to our Online Furniture Store, a Python-based application that simulates a fully functional e-commerce platform. The application includes inventory management, user profiles, a shopping cart, a checkout process, and order management, all implemented using object-oriented programming (OOP) principles.

<br> <br>

## 📜 Project Overview <br>
This project aims to:

* Simulate an e-commerce application for managing and selling furniture.
* Demonstrate the use of Python's OOP features, design patterns, and clean coding principles.
* Optimize data structures for efficient inventory and user management.
<br> The application is divided into the following components:
<br>
- Furniture Management <br>
- Inventory System <br>
- User Management <br>
- Shopping Cart <br>
- Order Management<br>
- API Integration <br>


------------------




## 🛠️ Features Implemented

### 1. Furniture Management
Base Classes: <br>
1.*DiscountStrategy* (Inherits from ABC) <br> 
This class defines different discount strategies that will be implemented later.
It has one abstract method - get_discount() and 4 derived classes(when every derived class implements get_discount accordingly).
To design this class, we used the Strategy Pattern.<br>
2. *Furniture* (Inherits from ABC) <br>
This class defines how a furniture instance looks like and relevant methods.
Attributes: u_id, name, description, material, color, wp, price(in $), dimensions, available_quantity, country of manufacture, type(default is "Generic"), discount_strategy(default is "NoDiscount") .<br>
Abstract methods:<br>
- calculate_discount()- (overridden in derived classes).<br>
- apply_discount()- (overridden in derived classes).<br>
Static method: price_with_discount() that returns the price after implementing the discount.<br>
Other class methods: <br>
1. apply_tax()- returns the price with the tax percentage.<br>
2. is_available() - checks if the furniture item is currently in stock.

- **Derived Classes:** <br>
        Chair, Table, Sofa, Bed, Wardrobe. <br>
        To enforce type-specific discount calculations- each class has unique attributes and a custom implementation of the 2 @abstractmethods - calculate_discount() and apply_discount(). In addition, every type of furniture has a unique implementation of string presentation for its' specific details.
        Example: Chairs with armrests receive an additional discount and have a method called chair_info() that returns its chair-specific details.<br>

- **Data Structure Choice:** <br>
        We used inheritance to ensure reusability and modularity, allowing for easy extension of new furniture types- We chose the Factory Pattern to support that -for this, we defined a class called FurnitureFactory to handle different inputs of furniture types.<br>
        
---------

### 2. Inventory System

**Class: Inventory**

Stores all furniture items grouped by type in a dictionary (items_by_type dictionary of dictionaries). <br>
Supports efficient lookups, updates, and search functionality. <br>

- **Key Methods:** <br>
        add_item: Adds items to the inventory, grouped by their type.<br>
        remove_item: Removes items based on their name and type.<br>
        search_by_type: Retrieves all items of a specific type.<br>
        check_low_stock: Alerts when stock levels fall below a defined threshold.<br>

- **Data Structure Choice:** <br>
        Nested Dictionary:  Format : {type: {name: Furniture}}. <br>
                - Outer dictionary: Keys represent furniture types (e.g., "Chair"). <br>
                - Inner dictionary: Maps item names to Furniture objects.<br>
        Reasoning: Facilitates efficient type-based and name-based lookups (O(1) for each level).<br>

----------


### 3. User Management

**Class: User** <br>

Attributes: name, email, password (hashed), address, wishlist, order_history. <br>

- **Key Methods:**<br>
        register_user and login_user: Handle user registration and authentication.<br>
        add_to_wishlist: Allows users to save items for future purchases.<br>
        view_order_history: Displays all orders placed by the user.<br>

- **Data Structure Choice:** <br>
        - List for Order History:<br>
                - The User class uses a list to store a user's order history. <br>
                - This choice ensures: <br>
                        - Ordered Data: Orders are naturally stored in chronological order.<br>
                        - Ease of Retrieval: Simple iteration for displaying all past orders.<br>
                        - Flexibility: Supports appending new orders seamlessly.<br>


- **Possible Enhancements:**<br>
        - Wishlist: Tracks items users are interested in, stored as a list in the User class for simplicity.<br>

--------

### 4. Shopping Cart

**Class: ShoppingCart**

Attributes: user, cart_items.

- **Key Methods:**<br>
        add_item and remove_item: Manage items in the cart. <br>
        calculate_total: Computes the total price before discounts.<br>
        apply_discount: Applies type-specific discounts and cart-wide promotional discounts.<br>
        checkout: Validates items, processes payment (mocked), and finalizes the order.<br>
  
- **Data Structure Choice:** <br>
        - Dictionary for Cart Items:<br>
                - Keys: Furniture objects.<br>
                - Values: Quantities of each item.<br>
        - Reasoning: Supports efficient updates and lookups for items in the cart.<br>

- During the checkout process, the items in the cart are: <br>
        - Validated: Ensure that the requested quantities are available in the inventory. <br>
        - Passed to the Order: These items are directly passed to the Order object.<br>



-----------


### 5. Order Management

**Class: Order**

Attributes: order_id, user, items (the dictionary of ordered items) , total_price, status.


- **Key Features:** <br>
        - Automatically generates a unique order ID using uuid.<br>
        - Stores items purchased and their quantities.<br>
        - Tracks the order status (e.g., "Pending", "Completed").<br>

        
- **Data Structure Choice:**<br>
        - Order History: Stored as a list in the User class, enabling easy retrieval and iteration.<br>



-------

### 6. API 

        TODO        ????? 

----------
----------



## 🧠 Design Choices and Optimizations - Summary 

#### Object-Oriented Design:

Leveraged inheritance and polymorphism for reusable and modular code.<br>
Abstract base class (Furniture) enforces consistent discount logic.<br>



#### Data Structures:<br>

Nested dictionaries in Inventory for efficient grouping and retrieval.<br>
Dictionaries in ShoppingCart and UserManager for quick lookups.<br>
Lists for order history and wishlists for simplicity.<br>


#### Efficiency: <br>

Avoided redundant iterations by grouping items by type.<br>
Used lazy evaluations (e.g., filtering only when needed).<br>


#### Security:

Stored hashed passwords for users using hashlib.<br>




------------
------------








