from abc import ABC, abstractmethod


class Furniture(ABC):
    """
     Base class to represent general furniture items.
     This class serves as a foundation for all specific furniture types.
     """

    def __init__(self, name: str, description: str, price: float, dimensions: tuple):
        """
        Initialize a Furniture object.

        :param name: Name of the furniture item.
        :param description: A brief description of the item.
        :param price: Price of the item in USD.
        :param dimensions: Tuple representing the dimensions (length, width, height) in cm.
        """
        self.name = name
        self.description = description
        self.price = price
        self.dimensions = dimensions
        self.available_quantity = 0
        self.type = "Generic"

    @abstractmethod
    def calculate_discount(self, discount: float) -> float:
        """
        Abstract method to calculate the discounted price of the item.
        Subclasses must provide their implementation.

        :param discount: Discount percentage to apply (e.g., 10 for 10%).
        :return: Discounted price of the item.
        """
        pass

    def apply_tax(self, tax_percentage: float) -> float:
        """
        Calculate the price after applying tax.

        :param tax_percentage: Tax percentage to apply (e.g., 15 for 15%).
        :return: Price of the item after tax is added.
        """
        return self.price * (1 + tax_percentage / 100)

    def is_available(self) -> bool:
        """
        Check if the item is available in stock.

        :return: True if available_quantity > 0, otherwise False.
        """
        return self.available_quantity > 0


# Derived Furniture Classes
class Chair(Furniture):
    """
    Represents a Chair.
    """

    def __init__(self, name: str, description: str, price: float, dimensions: tuple, has_armrests: bool, material: str):
        """
        Initialize a Chair object.

        :param name: Name of the chair.
        :param description: A brief description of the chair.
        :param price: Price of the chair in USD.
        :param dimensions: Tuple representing the dimensions (length, width, height) in cm.
        :param has_armrests: Boolean indicating if the chair has armrests.
        :param material: Material of the chair (e.g., wood, plastic).
        """
        super().__init__(name, description, price, dimensions)
        self.has_armrests = has_armrests
        self.material = material
        self.type = "Chair"

    def calculate_discount(self, base_discount: float) -> float:
        """
        Calculate the discounted price of the chair.

        :param base_discount: Discount percentage to apply (e.g., 10 for 10%).
        :return: Discounted price of the chair.
        """
        additional_discount = 5 if self.has_armrests else 0
        total_discount = base_discount + additional_discount
        return self.price * (1 - total_discount / 100)

    def chair_info(self):
        """Return chair-specific details."""
        return f"{self.name}: Armrests - {self.has_armrests}, Material - {self.material}"


class Table(Furniture):
    """
    Represents a Table.
    """

    def __init__(self, name: str, description: str, price: float, dimensions: tuple, shape: str, is_extendable: bool = False):
        """
        Initialize a Table object.

        :param name: Name of the table.
        :param description: A brief description of the table.
        :param price: Price of the table in USD.
        :param dimensions: Tuple representing the dimensions (length, width, height) in cm.
        :param shape: Shape of the table (e.g., rectangular, circular).
        :param is_extendable: Boolean indicating if the table can expand to become larger.
        """
        super().__init__(name, description, price, dimensions)
        self.shape = shape  # Shape of the table (e.g., rectangular, circular)
        self.is_extendable = is_extendable  # Indicates if the table can expand
        self.type = "Table"

    def calculate_discount(self, seasonal_discount: float) -> float:
        """
        Calculate the discounted price of the Table.

        :param seasonal_discount: Seasonal discount percentage to apply.
        :return: Discounted price of the chair.
        """
        extra_discount = 10 if self.is_extendable else 0
        total_discount = seasonal_discount + extra_discount
        return self.price * (1 - total_discount / 100)


class Sofa(Furniture):
    """
    Represents a Sofa.
    """

    def __init__(self, name: str, description: str, price: float, dimensions: tuple, num_seats: int,
                 has_recliner: bool):
        """
        Initialize a Sofa object.

        :param name: Name of the sofa.
        :param description: A brief description of the sofa.
        :param price: Price of the sofa in USD.
        :param dimensions: Tuple representing the dimensions (length, width, height) in cm.
        :param num_seats: Number of seats the sofa has.
        :param has_recliner: Boolean indicating if the sofa has a reclining feature.
        """
        super().__init__(name, description, price, dimensions)
        self.num_seats = num_seats  # Number of seats in the sofa
        self.has_recliner = has_recliner  # Whether the sofa has a reclining feature
        self.type = "Sofa"

    def calculate_discount(self, holiday_discount: float) -> float:
        """
        Calculate the discounted price for the sofa.

        :param holiday_discount: Holiday discount percentage to apply.
        :return: Discounted price of the sofa.
        """
        seat_based_discount = self.num_seats * 2  # 2% per seat
        total_discount = min(holiday_discount + seat_based_discount, 50)  # Cap at 50%
        return self.price * (1 - total_discount / 100)

    def sofa_info(self):
        """Return sofa-specific details."""
        return f"{self.name}: Seats - {self.num_seats}, Recliner - {self.has_recliner}"


class Bed(Furniture):
    """
    Represents a Bed.
    """

    def __init__(self, name: str, description: str, price: float, dimensions: tuple, bed_size: str, has_storage: bool):
        """
        Initialize a Bed object.

        :param name: Name of the bed.
        :param description: A brief description of the bed.
        :param price: Price of the bed in USD.
        :param dimensions: Tuple representing the dimensions (length, width, height) in cm.
        :param bed_size: Size of the bed (e.g., single, double, queen, king).
        :param has_storage: Boolean indicating if the bed includes storage space.
        """
        super().__init__(name, description, price, dimensions)
        self.bed_size = bed_size  # Size of the bed (e.g., single, double, queen, king)
        self.has_storage = has_storage  # Whether the bed includes storage space
        self.type = "Bed"

    def calculate_discount(self, member_discount: float) -> float:
        """
        Calculate the discounted price for the bed.

        :param member_discount: Discount percentage for loyalty program members.
        :return: Discounted price of the bed.
        """
        storage_discount = 15 if self.has_storage else 0
        total_discount = member_discount + storage_discount
        return self.price * (1 - total_discount / 100)

    def bed_info(self):
        """Return bed-specific details."""
        return f"{self.name}: Size - {self.bed_size}, Storage - {self.has_storage}"


class Wardrobe(Furniture):
    """
    Represents a Wardrobe.
    """

    def __init__(self, name: str, description: str, price: float, dimensions: tuple, num_doors: int, has_mirror: bool):
        """
        Initialize a Wardrobe object.

        :param name: Name of the wardrobe.
        :param description: A brief description of the wardrobe.
        :param price: Price of the wardrobe in USD.
        :param dimensions: Tuple representing the dimensions (length, width, height) in cm.
        :param num_doors: Number of doors the wardrobe has.
        :param has_mirror: Boolean indicating if the wardrobe has a mirror.
        """
        super().__init__(name, description, price, dimensions)
        self.num_doors = num_doors  # Number of doors in the wardrobe
        self.has_mirror = has_mirror  # Whether the wardrobe has a mirror
        self.type = "Wardrobe"

    def calculate_discount(self, clearance_discount: float) -> float:
        """
        Calculate the discounted price for the wardrobe.

        :param clearance_discount: Clearance discount percentage to apply.
        :return: Discounted price of the wardrobe.
        """
        door_discount = self.num_doors * 3  # 3% per door
        total_discount = clearance_discount + door_discount
        return self.price * (1 - total_discount / 100)

    def wardrobe_info(self):
        """Return wardrobe-specific details."""
        return f"{self.name}: Doors - {self.num_doors}, Mirror - {self.has_mirror}"