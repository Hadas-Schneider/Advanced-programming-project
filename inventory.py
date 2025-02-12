from furniture import Furniture

class Inventory:
    """
       Manages the collection of furniture items in the store, using a nested dictionary structure.
       Items are grouped by their type for efficient search operations.
       Handles operations such as adding, removing, updating, and searching for items.
    """

    def __init__(self):
        """Initialize an empty inventory grouped by furniture type."""
        self.items_by_type = {}  # {type: {name: Furniture}}
    def bla(self):
        pass
    
    def add_item(self, item: Furniture):
        """
        Add a furniture item to the inventory or update its quantity if it already exists.

        :param item: The furniture object to be added.
        """
        furniture_type = item.type  # Get the class name as the type

        if furniture_type in self.items_by_type:
            if item.name in self.items_by_type[furniture_type]:
                self.items_by_type[furniture_type][item.name].available_quantity += item.available_quantity
            else:
                self.items_by_type[furniture_type][item.name] = item
        else:
            self.items_by_type[furniture_type] = {item.name: item}

    def remove_item(self, name: str, furniture_type: str):
        """
        Remove a furniture item from the inventory by name and type.

        :param name: Name of the furniture item to remove.
        :param furniture_type: Type of the furniture item (e.g., "Chair", "Table").
        """
        if furniture_type in self.items_by_type and name in self.items_by_type[furniture_type]:
            del self.items_by_type[furniture_type][name]
        else:
            print(f"Item '{name}' of type '{furniture_type}' not found in inventory.")

    def update_quantity(self, name: str, furniture_type: str, quantity: int):
        """
        Update the available quantity of a specific furniture item.

        :param name: Name of the furniture item to update.
        :param furniture_type: Type of the furniture item (e.g., "Chair", "Table").
        :param quantity: New quantity to set for the item.
        """
        if furniture_type in self.items_by_type and name in self.items_by_type[furniture_type]:
            self.items_by_type[furniture_type][name].available_quantity = quantity
        else:
            print(f"Item '{name}' of type '{furniture_type}' not found in inventory.")

    def search_by_type(self, furniture_type: str):
        """
        Search for all furniture items of a specific type.

        :param furniture_type: Type of the furniture to search for (e.g., "Chair", "Table").
        :return: List of items matching the type.
        """
        return list(self.items_by_type.get(furniture_type, {}).values())

    def search(self, **filters):
        """
        Search for furniture items based on given attributes.

        :param filters: Key-value pairs to filter the search (e.g., name='Chair').
        :return: List of items matching the filters.
        """
        results = []
        for type_items in self.items_by_type.values():
            for item in type_items.values():
                if all(getattr(item, attr, None) == value for attr, value in filters.items()):
                    results.append(item)
        return results

    def get_all_items(self):
        """
        Returns all items in the inventory, formatted for API output.
        """
        all_items = []
        for furniture_type, items in self.items_by_type.items():
            for name, item in items.items():
                all_items.append({
                    'id': item.u_id,
                    'name': item.name,
                    'description': item.description,
                    'material': item.material,
                    'color': item.color,
                    'warranty_period': item.wp,
                    'price': item.price,
                    'dimensions': item.dimensions,
                    'country': item.country,
                    'type': item.type,
                    'available_quantity': item.available_quantity
                })
        return all_items

    def view_inventory(self):
        """
        Display all furniture items grouped by type in the inventory.
        """
        if not self.items_by_type:
            print("The inventory is empty.")
            return

        print("Current Inventory:")
        for furniture_type, items in self.items_by_type.items():
            print(f"Type: {furniture_type}")
            for name, item in items.items():
                print(f"  - {name}: {item.available_quantity} in stock, Price: ${item.price:.2f}")

    # extra method
    def check_low_stock(self, threshold=5):
        """
        Check for items with low stock.
        :param threshold: Stock quantity threshold.
        :return: List of low-stock items.
        """
        low_stock_items = []
        for item_type, type_items in self.items_by_type.items():
            for item in type_items.values():
                if item.available_quantity <= threshold:
                    low_stock_items.append(item)
        return low_stock_items
