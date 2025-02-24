from abc import ABC, abstractmethod


class DiscountStrategy(ABC):
    """
    Abstract base class for discount strategies.
    """
    @abstractmethod
    def get_discount(self) -> float:
        pass


class NoDiscount(DiscountStrategy):
    def get_discount(self) -> float:
        return 0


class HolidayDiscount(DiscountStrategy):
    def get_discount(self) -> float:
        return 15


class VIPDiscount(DiscountStrategy):
    def get_discount(self) -> float:
        return 20


class ClearanceDiscount(DiscountStrategy):
    def get_discount(self) -> float:
        return 30


class Furniture(ABC):
    """
     Base class to represent general furniture items.
     This class serves as a foundation for all specific furniture types.
     """

    def __init__(self, u_id: str, name: str, description: str, material: str, color: str, wp: int,
                 price: float, dimensions: tuple, country: str, available_quantity: int = 0,
                 discount_strategy: DiscountStrategy = NoDiscount()):
        """
        Initialize a Furniture object.

        param u_id: Unique id of the furniture
        param name: Name of the furniture item.
        param description: A brief description of the item.
        param material: Material of the furniture (e.g., wood, plastic).
        param color: Color of the furniture.
        param wp: Warranty Period (in years) of the furniture.
        param price: Price of the item in USD.
        param dimensions: Tuple representing the dimensions (length, width, height) in cm.
        param available_quantity : int representing the current available quantity of the item.
        param country: Where the furniture from.
        param type: str representing the item's type.
        param discount_strategy : representing the discount the item should have( the default is No Discount).

        """
        self.u_id = u_id
        self.name = name
        self.description = description
        self.material = material
        self.color = color
        self.wp = wp
        self.price = price
        self.dimensions = dimensions
        self.available_quantity = available_quantity
        self.country = country
        self.type = "Generic"
        self.discount_strategy = discount_strategy

    def set_discount_strategy(self, discount_strategy: DiscountStrategy):
        self.discount_strategy = discount_strategy

    @abstractmethod
    def calculate_discount(self, discount_strategy: DiscountStrategy) -> float:
        pass

    @abstractmethod
    def apply_discount(self, discount: float) -> float:
        pass

    @staticmethod
    def price_with_discount(price: float, discount: float) -> float:
        return round(price * (1 - discount / 100), 1)

    def apply_tax(self, tax_percentage: float) -> float:
        return self.price * (1 + tax_percentage / 100)

    def is_available(self) -> bool:
        """
        Check if the item is available in stock.

        return: True if available_quantity > 0, otherwise False.
        """
        if self.available_quantity < 1:
            print(f"Sorry, item '{self.name}' not in stock.")
            return False
        return True


# Derived Furniture Classes
class Chair(Furniture):
    """
    Represents a Chair.
    """
    def __init__(self, u_id: str, name: str, description: str, material: str, color: str, wp: int,
                 price: float, dimensions: tuple, country: str, available_quantity: int, has_armrests: bool):
        """
        Initialize a Chair object.

        param u_id: Unique id of the chair.
        param name: Name of the chair item.
        param description: A brief description of the chair.
        param material: Material of the chair (e.g., wood, plastic).
        param color: Color of the chair.
        param wp: Warranty Period (in years) of the chair.
        param price: Price of the chair in USD.
        param dimensions: Tuple representing the dimensions of the chair (length, width, height) in cm.
        param country: Where the furniture from.
        param available_quantity: int representing the current available quantity of the chair.
        param has_armrests: Boolean indicating if the chair has armrests.
        """
        super().__init__(u_id, name, description, material, color, wp, price, dimensions, country, available_quantity)
        self.has_armrests = has_armrests
        self.type = "Chair"

    def calculate_discount(self, discount_strategy: DiscountStrategy) -> float:
        """
        Calculate the discounted percent of the chair.

        param discount_strategy: Discount percentage base on the DiscountStrategy.
        return: total discount percent of the chair.
        """
        additional_discount = 5 if self.has_armrests else 0
        total_discount = min(discount_strategy.get_discount() + additional_discount, 50)  # Cap at 50%
        return total_discount

    def apply_discount(self, discount_strategy: DiscountStrategy) -> float:
        """
        Apply the discounted percent on the price of the chair.

        param discount_strategy: Discount percentage base on the DiscountStrategy.
        return: Discounted price of the chair.
        """
        total_discount = self.calculate_discount(discount_strategy)
        return Furniture.price_with_discount(self.price, total_discount)

    def chair_info(self):
        """Return chair-specific details."""
        return f"{self.name}: Armrests - {self.has_armrests}, Material - {self.material}"


class Table(Furniture):
    """
    Represents a Table.
    """

    def __init__(self, u_id: str, name: str, description: str, material: str, color: str, wp: int,
                 price: float, dimensions: tuple, country: str, available_quantity: int, shape: str,
                 is_extendable: bool = False):
        """
        Initialize a Table object.

        param u_id: Unique id of the table.
        param name: Name of the table item.
        param description: A brief description of the table.
        param material: Material of the table (e.g., wood, plastic).
        param color: Color of the table.
        param wp: Warranty Period (in years) of the table.
        param price: Price of the item in USD.
        param dimensions: Tuple representing the dimensions of the table (length, width, height) in cm.
        param country: Where the table from.
        param available_quantity: int representing the current available quantity of the table.
        param shape: Shape of the table (e.g., rectangular, circular).
        param is_extendable: Boolean indicating if the table can expand to become larger.
        """
        super().__init__(u_id, name, description, material, color, wp, price, dimensions, country, available_quantity)
        self.shape = shape  # Shape of the table (e.g., rectangular, circular)
        self.is_extendable = is_extendable  # Indicates if the table can expand
        self.type = "Table"

    def calculate_discount(self, discount_strategy: DiscountStrategy) -> float:
        """
        Calculate the discounted percent of the Table.

        param discount_strategy: Discount percentage base on the DiscountStrategy.
        return: total discount percent of the table.
        """
        additional_discount = 10 if self.is_extendable else 0
        total_discount = min(discount_strategy.get_discount() + additional_discount, 50)  # Cap at 50%
        return total_discount

    def apply_discount(self, discount_strategy: DiscountStrategy) -> float:
        """
        Apply the discounted percent on the price of the table.

        param discount_strategy: Discount percentage base on the DiscountStrategy.
        return: Discounted price of the table.
        """
        total_discount = self.calculate_discount(discount_strategy)
        return Furniture.price_with_discount(self.price, total_discount)

    def table_info(self):
        """Return table-specific details."""
        return f"{self.name}: Shape - {self.shape}, Extendable - {'Yes' if self.is_extendable else 'No'}, Material: " \
               f"{self.material}"


class Sofa(Furniture):
    """
    Represents a Sofa.
    """

    def __init__(self, u_id: str, name: str, description: str, material: str, color: str, wp: int,
                 price: float, dimensions: tuple, country: str, available_quantity: int, num_seats: int, has_recliner: bool):
        """
        Initialize a Sofa object.

        param u_id: Unique id of the sofa.
        param name: Name of the sofa item.
        param description: A brief description of the sofa.
        param material: Material of the sofa (e.g., wood, plastic).
        param color: Color of the sofa.
        param wp: Warranty Period (in years) of the sofa.
        param price: Price of the sofa in USD.
        param dimensions: Tuple representing the dimensions of the sofa (length, width, height) in cm.
        param country: Where the sofa from.
        param available_quantity: int representing the current available quantity of the sofa.
        param num_seats: Number of seats the sofa has.
        param has_recliner: Boolean indicating if the sofa has a reclining feature.
        """
        super().__init__(u_id, name, description, material, color, wp, price, dimensions, country, available_quantity)
        self.num_seats = num_seats  # Number of seats in the sofa
        self.has_recliner = has_recliner  # Whether the sofa has a reclining feature
        self.type = "Sofa"

    def calculate_discount(self, discount_strategy: DiscountStrategy) -> float:
        """
        Calculate the discounted percent of the Sofa.

        param discount_strategy: Discount percentage base on the DiscountStrategy.
        return: total discount percent of the sofa.
        """
        seat_based_discount = self.num_seats * 2  # 2% per seat
        total_discount = min(discount_strategy.get_discount() + seat_based_discount, 50)  # Cap at 50%
        return total_discount

    def apply_discount(self, discount_strategy: DiscountStrategy) -> float:
        """
        Apply the discounted percent on the price of the sofa.

        param discount_strategy: Discount percentage base on the DiscountStrategy.
        return: Discounted price of the sofa.
        """
        total_discount = self.calculate_discount(discount_strategy)
        return Furniture.price_with_discount(self.price, total_discount)

    def sofa_info(self):
        """Return sofa-specific details."""
        return f"{self.name}: Seats - {self.num_seats}, Recliner - {self.has_recliner}"


class Bed(Furniture):
    """
    Represents a Bed.
    """

    def __init__(self, u_id: str, name: str, description: str, material: str, color: str, wp: int,
                 price: float, dimensions: tuple, country: str, available_quantity: int, bed_size: str, has_storage: bool):
        """
        Initialize a Bed object.

        param u_id: Unique id of the bed.
        param name: Name of the furniture bed.
        param description: A brief description of the bed.
        param material: Material of the bed (e.g., wood, plastic).
        param color: Color of the bed.
        param wp: Warranty Period (in years) of the bed.
        param price: Price of the bed in USD.
        param dimensions: Tuple representing the dimensions of the bed (length, width, height) in cm.
        param country: Where the bed from.
        param available_quantity: int representing the current available quantity of the bed.
        param bed_size: Size of the bed (e.g., single, double, queen, king).
        param has_storage: Boolean indicating if the bed includes storage space.
        """
        super().__init__(u_id, name, description, material, color, wp, price, dimensions, country, available_quantity)
        self.bed_size = bed_size  # Size of the bed (e.g., single, double, queen, king)
        self.has_storage = has_storage  # Whether the bed includes storage space
        self.type = "Bed"

    def calculate_discount(self, discount_strategy: DiscountStrategy) -> float:
        """
        Calculate the discounted percent of the bed.

        param discount_strategy: Discount percentage base on the DiscountStrategy.
        return: total discount percent of the bed.
        """
        storage_discount = 15 if self.has_storage else 0
        total_discount = min(discount_strategy.get_discount() + storage_discount, 50)  # Cap at 50%
        return total_discount

    def apply_discount(self, discount_strategy: DiscountStrategy) -> float:
        """
        Apply the discounted percent on the price of the table.

        param discount_strategy: Discount percentage base on the DiscountStrategy.
        return: Discounted price of the table.
        """
        total_discount = self.calculate_discount(discount_strategy)
        return Furniture.price_with_discount(self.price, total_discount)

    def bed_info(self):
        """Return bed-specific details."""
        return f"{self.name}: Size - {self.bed_size}, Storage - {self.has_storage}"


class Wardrobe(Furniture):
    """
    Represents a Wardrobe.
    """

    def __init__(self, u_id: str, name: str, description: str, material: str, color: str, wp: int,
                 price: float, dimensions: tuple, country: str, available_quantity: int, num_doors: int, has_mirror: bool):
        """
        Initialize a Wardrobe object.

        param u_id: Unique id of the wardrobe.
        param name: Name of the wardrobe item.
        param description: A brief description of the wardrobe.
        param material: Material of the wardrobe (e.g., wood, plastic).
        param color: Color of the wardrobe.
        param wp: Warranty Period (in years) of the wardrobe.
        param price: Price of the wardrobe in USD.
        param dimensions: Tuple representing the dimensions of the wardrobe (length, width, height) in cm.
        param country: Where the wardrobe from.
        param available_quantity: int representing the current available quantity of the wardrobe.
        param num_doors: Number of doors the wardrobe has.
        param has_mirror: Boolean indicating if the wardrobe has a mirror.
        """
        super().__init__(u_id, name, description, material, color, wp, price, dimensions, country, available_quantity)
        self.num_doors = num_doors  # Number of doors in the wardrobe
        self.has_mirror = has_mirror  # Whether the wardrobe has a mirror
        self.type = "Wardrobe"

    def calculate_discount(self, discount_strategy: DiscountStrategy) -> float:
        """
        Calculate the discounted percent of the wardrobe.

        param discount_strategy: Discount percentage base on the DiscountStrategy.
        return: total discount percent of the wardrobe.
        """
        door_discount = self.num_doors * 3  # 3% per door
        total_discount = min(discount_strategy.get_discount() + door_discount, 50)  # Cap at 50%
        return total_discount

    def apply_discount(self, discount_strategy: DiscountStrategy) -> float:
        """
        Apply the discounted percent on the price of the wardrobe.

        param discount_strategy: Discount percentage base on the DiscountStrategy.
        return: Discounted price of the wardrobe.
        """
        total_discount = self.calculate_discount(discount_strategy)
        return Furniture.price_with_discount(self.price, total_discount)

    def wardrobe_info(self):
        """Return wardrobe-specific details."""
        return f"{self.name}: Doors - {self.num_doors}, Mirror - {self.has_mirror}"


# Factory Pattern Implementation
class FurnitureFactory:
    """
    Factory class for creating furniture dynamically.
    This class should not be instantiated.
    """

    @staticmethod
    def create_furniture(furniture_type, **kwargs):
        defaults = {
            "available_quantity": 0,
            "color": "Black",
            "material": "Wood",
            "u_id": "00",
            "description": "None",
            "wp": 5,
            "price": 100.0,
            "dimensions": (50, 50, 50),
            "country": "USA"
        }
        defaults.update(kwargs)

        if furniture_type == "Chair":
            return Chair(**defaults)
        elif furniture_type == "Table":
            return Table(**defaults)
        elif furniture_type == "Sofa":
            return Sofa(**defaults)
        elif furniture_type == "Bed":
            return Bed(**defaults)
        elif furniture_type == "Wardrobe":
            return Wardrobe(**defaults)
        else:
            raise ValueError(f"Unknown furniture type: {furniture_type}")
