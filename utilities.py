import backend


class Basket:
    """
    Data structure that acts as a virtual basket until the user logs out
    """
    def __init__(self):
        self.products = []
        self.subtotal = 0
        self.delivery_cost = 2.5
        self.total = 0

    def add(self, product_details: dict):
        """
        Adds a product to the basket

        Parameters
        ----------
        product_details : dict
            A dictionary of the product attributes.
            Keys should state the attribute names.
            Values should state the attributes themselves.
        """
        self.products.append(product_details)

    def reset_basket(self):
        self.products = []

    def delete_product(self, bin_product: dict):
        """
        Deletes a specified product from the basket

        Parameters
        ----------
        bin_product : dict
            A dictionary of the product attributes of the item to delete.
            Keys should state the attribute names.
            Values should state the attributes themselves.
        """
        self.products.remove(bin_product)

    def update_quantity(self, product_id: int, quantity: int):
        """
        Updates the quantity of a specified product within the basket and automatically updates subtotal

        Parameters
        ----------
        product_id : int
            The identifier for the product whose quantity should be updated

        quantity : int
            The new quantity
        """
        for product in self.products:
            if product.get("product_id") == product_id:
                product["quantity"] = quantity
        self.update_subtotal()

    def update_subtotal(self):
        """
        Updates the subtotal (and consequently total) of the basket
        """
        self.subtotal = backend.calculate_subtotal(self.products)
        self.total = self.subtotal + self.delivery_cost

    def set_delivery_cost(self, delivery_cost):
        """
        Setter method for the delivery cost attribute

        Parameters
        ----------
        delivery_cost : int, float
            The new delivery cost attribute
        """
        self.delivery_cost = delivery_cost
        self.total = delivery_cost + self.subtotal

    def get_delivery_cost(self):
        return self.delivery_cost

    def get_subtotal(self):
        """
        Get the basket's subtotal cost

        Returns
        -------
        int, float
            The subtotal for the basket
        """
        return self.subtotal

    def get_total(self):
        """
        Gets the basket's total cost

        Returns
        -------
        int | float
            The total for the basket
        """
        return self.total

    def get_products(self):
        """
        Get all products within the basket

        Returns
        -------
        list
            The products currently in the basket
        """
        return self.products


class CompareBucket:
    """
    Data structure that stores products for comparison until the user logs out
    """
    def __init__(self):
        self.products = []

    def reset(self):
        self.products = []

    def get_products(self):
        return self.products

    def add_product(self, product: dict):
        """
        Adds a product to the comparison system
        """
        # If product is already in the system
        if self.search(product.get("product_id")):
            return 1
        # If the comparison system is full
        if len(self.products) >= 2:
            return 2
        else:
            # Add product to system
            self.products.append(product)
            return 0

    def get_blanks(self):
        """
        Return how many slots are left in the comparison system
        """
        return 2 - len(self.products)

    def delete_product(self, product_id=None):
        """
        Deletes the product with a given product_id.
        If no product_id is specified, the most recent product added will be deleted

        Parameters
        ----------
        product_id : int
            The id of the product to be deleted
        """
        if product_id:
            match_product = self.search(product_id)
            if match_product:
                self.products.remove(match_product)
                return match_product
        else:
            if len(self.products) != 0:
                removed_product = self.products.pop()
                return removed_product

    def search(self, product_id: int):
        """
        Searches to see if a product is in the comparison system

        Parameters
        ----------
        product_id : int
            The ID of the product

        Returns
        -------
        dict | None
            The product found, or None if no product is found
        """
        for product in self.products:
            if product.get("product_id") == product_id:
                return product
        return None


class Colours:
    """
    Data structure to store the colour scheme of the application
    """
    def __init__(self):
        self.primary_colour = "#FFE156"
        self.bg_colour = "#FFFFFF"
        self.button_colour = "#FFE156"
        self.hover_colour = "#FFB565"
        self.disabled_entry_colour = "#979DA2"

    def get_primary_colour(self):
        return self.primary_colour

    def get_bg_colour(self):
        return self.bg_colour

    def get_button_colour(self):
        return self.button_colour

    def get_hover_colour(self):
        return self.hover_colour

    def get_disabled_entry_colour(self):
        return self.disabled_entry_colour
