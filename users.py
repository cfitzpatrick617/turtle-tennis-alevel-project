import crud_functionality as crud
import utilities as util


class User:
    """
    Superclass to define attributes and methods for all users of the system

    Parameters
    ----------
    personal_id : int
        The ID of the user

    username : str
        The user's username

    name : str
        The user's first name

    surname : str
        The user's last name

    email_address : str
        The user's email address
    """
    def __init__(self,
                 personal_id: int,
                 username: str,
                 name: str,
                 surname: str,
                 email_address: str):
        self.personal_id = personal_id
        self.username = username
        self.name = name
        self.surname = surname
        self.email_address = email_address

    def get_name(self):
        return self.name

    def get_surname(self):
        return self.surname

    def get_personal_id(self):
        return self.personal_id

    def get_email(self):
        return self.email_address


class Customer(User):
    """
    Subclass of user which defines unique attributes and methods for all customers of the system

    Parameters
    ----------
    customer_details : dict
        The personal attributes of the customer using the system.
        Keys should state the attribute name.
        Values should state the value for the corresponding attribute
    """
    def __init__(self,
                 customer_details: dict):
        super().__init__(customer_details.get("customer_id"),
                         customer_details.get("username"),
                         customer_details.get("name"),
                         customer_details.get("surname"),
                         customer_details.get("email_address"))
        self.basket = util.Basket()
        self.compare_bucket = util.CompareBucket()

    def get_basket(self):
        return self.basket

    def get_compare_bucket(self):
        return self.compare_bucket

    def refresh_details(self):
        # Get the most up to date customer details from the database
        account_details = crud.search_table("ecommerce",
                                            "Customer",
                                            ["*"],
                                            f"customer_id = {self.personal_id}")[0]
        # Reset the stored details to the most up to date versions
        self.username = account_details.get("username")
        self.name = account_details.get("name")
        self.surname = account_details.get("surname")
        self.email_address = account_details.get("email_address")


class Staff(User):
    def __init__(self,
                 staff_details: dict):
        super().__init__(staff_details.get("staff_id"),
                         staff_details.get("username"),
                         staff_details.get("name"),
                         staff_details.get("surname"),
                         staff_details.get("email_address"))
        self.access_level = staff_details.get("access_level")

    def get_access_level(self):
        return self.access_level
