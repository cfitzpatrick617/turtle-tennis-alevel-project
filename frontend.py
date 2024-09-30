# Built-in libraries
import _tkinter
import threading
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as mbox
from tkinter.filedialog import askopenfilename
import time
import timeit
from typing import Literal
import warnings

# External libraries
import customtkinter as ctk

# Custom libraries
import backend
import crud_functionality as crud
import custom_widgets as cWidget
import utilities as util
import users

# Display settings
ctk.FontManager.load_font("Poppins-Regular.ttf")
ctk.FontManager.load_font("Inter-Regular.ttf")
ctk.set_appearance_mode("light")

colours = util.Colours()


class RootWindow(ctk.CTk):
    """
    The main application window
    """
    def __init__(self):
        super().__init__(fg_color=colours.get_primary_colour())
        self.st = timeit.default_timer()
        self.geometry("900x600")
        self.title("Turtle Tennis")
        try:
            self.iconbitmap(backend.get_directory("images") + "turtle_tennis_icon_ICON_ONLY.ico")
        except _tkinter.TclError:
            pass
        self.propagate(False)
        self.current_user = None

        self.summary_report_manager = None
        self.image_manager = None
        self.customer_sidebar = cWidget.AccountSidebar(self, self)
        self.staff_sidebar = cWidget.StaffSidebar(self, self)

        # Create a loading message whilst the application is initialising
        loading_frame = cWidget.Frame(self, fg_color=colours.get_primary_colour())
        loading_frame.place(x=0, y=0, relwidth=1, relheight=1)
        loading_frame.grid_rowconfigure(0, weight=1)
        loading_frame.grid_rowconfigure(1, weight=1)
        loading_frame.grid_columnconfigure(0, weight=1)
        heading_label = cWidget.Label(loading_frame,
                                      fg_color=colours.get_primary_colour(),
                                      text="Welcome to Turtle Tennis.",
                                      font=("Poppins Regular", 48))
        heading_label.grid(row=0, column=0, sticky="S")
        subheading_label = cWidget.Label(loading_frame,
                                         fg_color=colours.get_primary_colour(),
                                         text="Starting up your application.",
                                         font=("Inter Regular", 32))
        subheading_label.grid(row=1, column=0, sticky="N")

        # Create all frames in their default state
        self.frames = {"WelcomeFrame": WelcomeFrame(self),
                       "LoginFrame": LoginFrame(self),
                       "RegisterFrame": RegisterFrame(self),
                       "BrowsingFrame": BrowsingFrame(self),
                       "ProductComparisonFrame": ProductComparisonFrame(self),
                       "ProductFrame": ProductFrame(self),
                       "BasketFrame": BasketFrame(self),
                       "CheckoutFrame": CheckoutFrame(self),
                       "MyProfileFrame": MyProfileFrame(self),
                       "MyCardsFrame": MyCardsFrame(self),
                       "MyOrdersFrame": MyOrdersFrame(self),
                       "PastOrderFrame": PastOrderFrame(self),
                       "ProcessingOrderFrame": ProcessingOrderFrame(self),
                       "ConfirmationFrame": ConfirmationFrame(self),
                       "DatabaseManagementFrame": DatabaseManagementFrame(self)}
        # Place all frames
        for frame in list(self.frames.values()):
            frame.place(x=0, y=0, relwidth=1, relheight=1)
        self.load_frame("WelcomeFrame")
        # self.load_frame("ProcessingOrderFrame")
        print(f"Time to start up: {timeit.default_timer() - self.st}s")

    def load_frame(self, frame_name: str, **kwargs):
        """
        Displays a given frame

        Parameters
        ------------
        frame_name : str
            The name of the frame which is to be raised
        """
        st = timeit.default_timer()
        frame = self.frames.get(frame_name)
        frame.refresh(**kwargs)
        frame.tkraise()
        print(f"Time to load {frame_name}: {timeit.default_timer() - st}s")

    def set_current_user(self, current_user):
        """
        Sets the current user of the application

        Parameters
        ----------
        current_user : object
            The current user's 'User' object
        """
        self.current_user = current_user

    def get_current_user(self):
        """
        Gets the 'User' object for the current user of the system

        Returns
        -------
        object
            The current user's 'User' object
        """
        return self.current_user

    def expand_image_manager(self, existing_image_file: str = ""):
        """
        Displays the image manager

        Returns
        -------
        any
            The image manager object
        """
        if self.image_manager is None or not self.image_manager.winfo_exists():
            self.image_manager = ImageController(self, self, existing_image_file)
        self.image_manager.grab_set()
        self.image_manager.wait_window()
        return self.image_manager.get_choice()

    def expand_summary_report_manager(self):
        """
        Displays the summary report manager

        Returns
        -------
        any
            The summary report manager object
        """
        if self.summary_report_manager is None or not self.summary_report_manager.winfo_exists():
            self.summary_report_manager = SummaryReportController(self, self)
        self.summary_report_manager.grab_set()
        return self.summary_report_manager

    def expand_customer_sidebar(self):
        """
        Causes the customer sidebar to emerge on-screen
        """
        self.customer_sidebar.expand()

    def expand_staff_sidebar(self):
        """
        Causes the staff sidebar to emerge on-screen
        """
        self.staff_sidebar.expand()

    def logout(self):
        """
        Logs out whoever is currently using the system
        """
        self.set_current_user(None)
        self.load_frame("WelcomeFrame")


class WelcomeFrame(cWidget.ParentFrame):
    """
    The screen that welcomes the user to the system i.e. the landing page

    Parameters
    ----------
    app : any
        The main window of the application
    """
    def __init__(self, app):
        super().__init__(app, fg_color=colours.get_primary_colour())
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Display welcome animation and subsequent options for advancement
        self.welcome_animation = cWidget.WelcomeAnimation(self, app)
        self.welcome_animation.grid(row=0, column=0)

    def refresh(self):
        """
        Resets the welcome screen
        """
        self.welcome_animation.start()


class RegisterFrame(cWidget.ParentFrame):
    """
    The screen that allows a user to register a new account

    Parameters
    ----------
    app : any
        The main window of the application
    """
    def __init__(self, app: any):
        super().__init__(app, fg_color=colours.get_primary_colour())
        self.app = app
        cWidget.UnborderedFilledButton(self,
                                       image_width=30,
                                       image_height=30,
                                       width=30,
                                       image_file="back_icon.png",
                                       command=lambda: self.app.load_frame("WelcomeFrame")).place(x=20, y=20)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1, uniform="uniform")
        self.grid_columnconfigure(1, weight=2, uniform="uniform")
        self.grid_columnconfigure(2, weight=1, uniform="uniform")

        def enter_details():
            """
            Validates entry and creates a new account if valid
            """
            entry_values = {field_name: entry_widget.get() for field_name, entry_widget in self.entry_widgets.items()}
            entry_validations = [entry_widget.check_if_valid() for entry_widget in self.entry_widgets.values()]
            if False not in entry_validations:
                crud.add_record("ecommerce",
                                "Customer",
                                entry_values)
                # Get the user's new record and assign that record as the current user of the system
                matched_accounts = crud.search_table("ecommerce",
                                                     "Customer",
                                                     ["*"],
                                                     f"username = '{backend.encrypt('username', entry_values['username'])}'")
                mbox.showinfo("Success!", "Account created successfully!")
                self.app.set_current_user(users.Customer(matched_accounts[0]))
                self.app.load_frame("BrowsingFrame")
            else:
                mbox.showerror("Error!", "Invalid input!")

        entry_frame = tk.Frame(self,
                               bg=colours.get_primary_colour())
        entry_frame.grid(row=0, column=1, pady=(25, 20), sticky="NSEW")

        # Configure row and column sizes of entryFrame
        entry_frame.grid_rowconfigure(0, weight=3, uniform="uniform")
        entry_frame.grid_rowconfigure(1, weight=1, uniform="uniform")
        entry_frame.grid_rowconfigure(2, weight=1, uniform="uniform")
        entry_frame.grid_rowconfigure(3, weight=1, uniform="uniform")
        entry_frame.grid_rowconfigure(4, weight=1, uniform="uniform")
        entry_frame.grid_rowconfigure(5, weight=1, uniform="uniform")
        entry_frame.grid_rowconfigure(6, weight=1, uniform="uniform")
        entry_frame.grid_rowconfigure(7, weight=2, uniform="uniform")
        entry_frame.grid_columnconfigure(0, weight=2, uniform="uniform")
        entry_frame.grid_columnconfigure(1, weight=2, uniform="uniform")

        # Label used to display the instruction message
        title_label = cWidget.Label(entry_frame,
                                    text="Create your account",
                                    font=("Poppins Regular", 48),
                                    max_line_length=15,
                                    fg_color=colours.get_primary_colour(),
                                    justify="center")
        title_label.grid(row=0, column=0, columnspan=2, sticky="N")

        # Form line 1 - Username and password label / entry field
        username_label = cWidget.Label(entry_frame,
                                       text="Username:",
                                       fg_color=colours.get_primary_colour())
        username_label.grid(row=1, column=0, pady=(0, 10), sticky="SW")
        username_entry = cWidget.Entry(entry_frame,
                                       table_name="Customer",
                                       field_name="username",
                                       bg_color=colours.get_primary_colour())
        username_entry.grid(row=2, column=0, padx=(0, 10), sticky="NEW")

        # Password label and entry field
        password_label = cWidget.Label(entry_frame,
                                       text="Password:",
                                       fg_color=colours.get_primary_colour())
        password_label.grid(row=1, column=1, padx=(10, 0), pady=(0, 10), sticky="SW")
        password_entry = cWidget.Entry(entry_frame,
                                       table_name="Customer",
                                       field_name="password",
                                       bg_color=colours.get_primary_colour())
        password_entry.grid(row=2, column=1, padx=(10, 0), sticky="NEW")

        # Form line 2 - Name and surname label / entry field
        name_label = cWidget.Label(entry_frame,
                                   text="Name:",
                                   fg_color=colours.get_primary_colour())
        name_label.grid(row=3, column=0, pady=(0, 10), sticky="SW")
        name_entry = cWidget.Entry(entry_frame,
                                   table_name="Customer",
                                   field_name="name",
                                   bg_color=colours.get_primary_colour())
        name_entry.grid(row=4, column=0, padx=(0, 10), sticky="NEW")

        # Surname label and entry field
        surname_label = cWidget.Label(entry_frame,
                                      text="Surname:",
                                      fg_color=colours.get_primary_colour())
        surname_label.grid(row=3, column=1, padx=(10, 0), pady=(0, 10), sticky="SW")
        surname_entry = cWidget.Entry(entry_frame,
                                      table_name="Customer",
                                      field_name="surname",
                                      bg_color=colours.get_primary_colour())
        surname_entry.grid(row=4, column=1, padx=(10, 0), sticky="NEW")

        # Form line 3 - Email label and email entry field
        email_label = cWidget.Label(entry_frame,
                                    text="Email:",
                                    fg_color=colours.get_primary_colour())
        email_label.grid(row=5, column=0, pady=(0, 10), sticky="SW")
        email_entry = cWidget.Entry(entry_frame,
                                    table_name="Customer",
                                    field_name="email_address",
                                    bg_color=colours.get_primary_colour())
        email_entry.grid(row=6, column=0, columnspan=2, sticky="NEW")

        self.entry_widgets = {"username": username_entry,
                              "password": password_entry,
                              "name": name_entry,
                              "surname": surname_entry,
                              "email_address": email_entry}

        # Button used to clear entry widgets
        clear_button = cWidget.FilledButton(entry_frame,
                                            text="Clear input",
                                            command=lambda: backend.clear_entry_widgets(list(self.entry_widgets.values())),
                                            width=150)
        clear_button.grid(row=7, column=0, padx=(0, 20), pady=20, sticky="EW")

        # Button used to create account
        create_button = cWidget.FilledButton(entry_frame,
                                             text="Create account",
                                             command=enter_details,
                                             width=150)
        create_button.grid(row=7, column=1, padx=(20, 0), pady=20, sticky="EW")

    def refresh(self):
        """
        Resets the register screen
        """
        backend.clear_entry_widgets(list(self.entry_widgets.values()))


class LoginFrame(cWidget.ParentFrame):
    """
    The screen that allows a user to login to an account

    Parameters
    ----------
    app : any
        The main window of the application
    """
    def __init__(self, app):
        super().__init__(app, fg_color=colours.get_primary_colour())
        self.app = app
        cWidget.UnborderedFilledButton(self,
                                       image_width=30,
                                       image_height=30,
                                       width=30,
                                       image_file="back_icon.png",
                                       command=lambda: self.app.load_frame("WelcomeFrame")).place(x=20, y=20)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1, uniform="uniform")
        self.grid_columnconfigure(1, weight=3, uniform="uniform")
        self.grid_columnconfigure(2, weight=1, uniform="uniform")

        def try_login():
            """
            Attempts to log the user in given the entry values
            """
            st = timeit.default_timer()
            username = username_entry.get()
            password = password_entry.get()

            user_type, matched_account = backend.try_login(username, password)
            if matched_account:
                if user_type == "Staff":
                    self.app.set_current_user(users.Staff(matched_account))
                    # Set starting tables for each access level
                    if matched_account.get("access_level") == "Management":
                        starting_table = "Customer"
                    else:
                        starting_table = "Orders"
                    self.app.load_frame("DatabaseManagementFrame", table_name=starting_table)
                else:
                    self.app.set_current_user(users.Customer(matched_account))
                    self.app.load_frame("BrowsingFrame")
                print(f"Time taken to login: {timeit.default_timer() - st}s")
                mbox.showinfo("Success!", "Login was successful!")
            else:
                mbox.showerror("Error!", "Username or password invalid.")
        
        entry_frame = tk.Frame(self,
                               bg=colours.get_primary_colour())
        entry_frame.grid(row=0, column=1, sticky="NS", pady=(25, 20))
        entry_frame.propagate(False)

        entry_frame.grid_rowconfigure(0, weight=2, uniform="uniform")
        entry_frame.grid_rowconfigure(1, weight=1, uniform="uniform")
        entry_frame.grid_rowconfigure(2, weight=1, uniform="uniform")
        entry_frame.grid_rowconfigure(3, weight=1, uniform="uniform")
        entry_frame.grid_rowconfigure(4, weight=1, uniform="uniform")
        entry_frame.grid_rowconfigure(5, weight=2, uniform="uniform")
        entry_frame.grid_columnconfigure(0, weight=2, uniform="uniform")
        entry_frame.grid_columnconfigure(1, weight=1, uniform="uniform")
        entry_frame.grid_columnconfigure(2, weight=2, uniform="uniform")

        title_label = cWidget.Label(entry_frame,
                                    text="Login to your account",
                                    font=("Poppins Regular", 48),
                                    max_line_length=15,
                                    justify="center",
                                    fg_color=colours.get_primary_colour())
        title_label.grid(row=0, column=0, columnspan=3, sticky="N")
        
        # Row 1 - Username label and entry widget
        username_label = cWidget.Label(entry_frame,
                                       text="Username:",
                                       fg_color=colours.get_primary_colour())
        username_label.grid(row=1, column=0, pady=(0, 10), sticky="SW")
        username_entry = cWidget.Entry(entry_frame,
                                       bg_color=colours.get_primary_colour(),
                                       validated=False)
        username_entry.grid(row=2, column=0, columnspan=3, sticky="EW")

        # Row 2 - Password label and entry widget
        password_label = cWidget.Label(entry_frame,
                                       text="Password:",
                                       fg_color=colours.get_primary_colour())
        password_label.grid(row=3, column=0, pady=(0, 10), sticky="SW")
        password_entry = cWidget.Entry(entry_frame,
                                       bg_color=colours.get_primary_colour(),
                                       hideable=True,
                                       validated=False)
        password_entry.grid(row=4, column=0, columnspan=3, sticky="EW")

        self.entry_widgets = [username_entry,
                              password_entry]

        # Row 3 - Login button / clear entry fields button
        clear_button = cWidget.FilledButton(entry_frame,
                                            text="Clear input",
                                            command=lambda: backend.clear_entry_widgets(self.entry_widgets))
        clear_button.grid(row=5, column=0, sticky="W")

        login_button = cWidget.FilledButton(entry_frame,
                                            text="Login",
                                            command=try_login)
        login_button.grid(row=5, column=2, sticky="E")

    def refresh(self):
        """
        Resets the login screen
        """
        backend.clear_entry_widgets(self.entry_widgets)


class BrowsingFrame(cWidget.ParentFrame):
    """
    The screen that allows a customer to browse for products

    Parameters
    ----------
    app : any
        The main window of the application
    """
    def __init__(self, app):
        super().__init__(app)
        self.app = app
        self.grid_rowconfigure(0, weight=2, uniform="uniform")
        self.grid_rowconfigure(1, weight=1, uniform="uniform")
        self.grid_rowconfigure(2, weight=7, uniform="uniform")
        self.grid_columnconfigure(0, weight=1, uniform="uniform")
        self.grid_columnconfigure(1, weight=4, uniform="uniform")

        self.product_view = cWidget.ProductView(self,
                                                self.app)
        self.product_view.grid(row=2, column=1, sticky="NSEW")

        # Top bar
        topbar = cWidget.Topbar(self, self.app)
        topbar.grid(row=0, column=0, columnspan=2, sticky="NSEW")
        self.searchbar = cWidget.Searchbar(topbar)
        self.searchbar.grid(row=0, column=1, sticky="EW")

        subheading_bar = cWidget.Frame(self)
        subheading_bar.grid(row=1, column=0, columnspan=2, sticky="NSEW")
        subheading_bar.grid_rowconfigure(0, weight=1)
        subheading_bar.grid_columnconfigure(0, weight=3, uniform="uniform")
        subheading_bar.grid_columnconfigure(1, weight=8, uniform="uniform")
        subheading_bar.grid_columnconfigure(2, weight=4, uniform="uniform")

        sidebar_icon_label = cWidget.Label(subheading_bar,
                                           text="Filters",
                                           image_file="filter_icon.png",
                                           image_width=50,
                                           image_height=50,
                                           font=("Poppins Regular", 24))
        sidebar_icon_label.grid(row=0, column=0, padx=10, sticky="W")

        sort_subheading = cWidget.Label(subheading_bar,
                                        text="Sort by:",
                                        anchor="e")
        sort_subheading.grid(row=0, column=1, padx=10, sticky="E")

        self.sort_categories = {"Default": [],
                                "Price (ascending)": ["sale_price", "asc"],
                                "Price (descending)": ["sale_price", "desc"],
                                "Rating (ascending)": ["average_rating", "asc"],
                                "Rating (descending)": ["average_rating", "desc"],
                                "Name (ascending)": ["name", "asc"],
                                "Name (descending)": ["name", "desc"],
                                "Supplier (ascending)": ["company_name", "asc"],
                                "Supplier (descending)": ["company_name", "desc"]}

        # NOTE: command defined after all widgets are created
        dropdown_frame = cWidget.Frame(subheading_bar,
                                       fg_color="#BDBDBD",
                                       border_width=1)
        dropdown_frame.grid(row=0, column=2, padx=10, sticky="EW")
        dropdown_frame.grid_rowconfigure(0, weight=1)
        dropdown_frame.grid_columnconfigure(0, weight=1)
        self.sort_dropdown = cWidget.Dropdown(dropdown_frame,
                                              values=list(self.sort_categories.keys()),
                                              var_default="Default")
        self.sort_dropdown.grid(row=0, column=0, padx=1, pady=1, sticky="NSEW")

        sidebar = cWidget.Frame(self)
        sidebar.grid(row=2, column=0, sticky="NSEW")
        sidebar.rowconfigure(0, weight=5, uniform="uniform")
        sidebar.rowconfigure(1, weight=6, uniform="uniform")
        sidebar.rowconfigure(2, weight=2, uniform="uniform")
        sidebar.rowconfigure(3, weight=2, uniform="uniform")
        sidebar.columnconfigure(0, weight=1)

        # Rating filter
        rating_frame = cWidget.Frame(sidebar)
        rating_frame.grid(row=1, column=0, pady=10, sticky="NSEW")
        rating_frame.grid_rowconfigure(0, weight=2, uniform="uniform")
        rating_frame.grid_rowconfigure(1, weight=1, uniform="uniform")
        rating_frame.grid_rowconfigure(2, weight=1, uniform="uniform")
        rating_frame.grid_rowconfigure(3, weight=1, uniform="uniform")
        rating_frame.grid_rowconfigure(4, weight=1, uniform="uniform")
        rating_frame.grid_rowconfigure(5, weight=1, uniform="uniform")

        self.radio_button_var = tk.StringVar(master=rating_frame, value="0+")  # change?
        self.checkboxes = {}

        rating_label = cWidget.Label(rating_frame,
                                     text="Rating:")
        rating_label.grid(row=0, column=0, padx=10, sticky="W")

        rating_scale = ["0+", "1+", "2+", "3+", "4+"]
        self.radio_buttons = []

        for count, step in enumerate(rating_scale):
            # NOTE: command defined after all widgets are created
            radio_button = ctk.CTkRadioButton(rating_frame,
                                              text=step,
                                              font=("Inter Regular", 20),
                                              variable=self.radio_button_var,
                                              value=step)
            radio_button.grid(row=count + 1, column=0, padx=10, sticky="W")
            self.radio_buttons.append(radio_button)
            if count == 0:
                # Sets the default rating to 0+
                radio_button.select()

        # Category filter
        category_frame = cWidget.Frame(sidebar)
        category_frame.grid(row=0, column=0, sticky="NSEW")
        category_frame.grid_rowconfigure(0, weight=1, uniform="uniform")
        category_frame.grid_rowconfigure(1, weight=1, uniform="uniform")
        category_frame.grid_rowconfigure(2, weight=1, uniform="uniform")
        category_frame.grid_rowconfigure(3, weight=1, uniform="uniform")
        category_frame.grid_rowconfigure(4, weight=1, uniform="uniform")

        category_title_label = cWidget.Label(category_frame,
                                             text="Categories:")
        category_title_label.grid(row=0, column=0, padx=10, sticky="W")

        categories = ["Rackets",
                      "Balls",
                      "Clothing",
                      "Equipment"]

        for count, category in enumerate(categories):
            check_var = tk.StringVar(category_frame, "off")
            # NOTE: command defined after all widgets are created
            category_checkbox = ctk.CTkCheckBox(category_frame,
                                                text=category,
                                                font=("Inter Regular", 20),
                                                variable=check_var,
                                                onvalue="on",
                                                offvalue="off")
            category_checkbox.grid(row=count + 1, column=0, padx=10, sticky="W")
            self.checkboxes[category] = category_checkbox

        # In stock filter
        stock_frame = cWidget.Frame(sidebar)
        stock_frame.grid(row=2, column=0, sticky="NSEW")
        stock_frame.grid_rowconfigure(0, weight=1)

        in_stock_label = cWidget.Label(stock_frame,
                                       text="In stock:")
        in_stock_label.grid(row=0, column=0, padx=10, sticky="W")

        self.stock_switch_var = tk.IntVar(stock_frame, value=1)

        # NOTE: command defined after all widgets are created
        self.stock_switch = ctk.CTkSwitch(stock_frame,
                                          text="",
                                          variable=self.stock_switch_var)
        self.stock_switch.select()
        self.stock_switch.grid(row=0, column=1, sticky="W")

        # NOTE: command defined after all widgets are created
        reset_filters_button = cWidget.FilledButton(sidebar,
                                                    text="Clear filters",
                                                    height=25,
                                                    bg_color="White")
        reset_filters_button.grid(row=3, column=0, padx=10, sticky="W")

        # Define commands for all widgets
        self.searchbar.set_search_command(self.apply_filters_and_sort)
        for checkbox in self.checkboxes.values():
            checkbox.configure(command=self.apply_filters_and_sort)
        for radio_button in self.radio_buttons:
            radio_button.configure(command=self.apply_filters_and_sort)
        self.stock_switch.configure(command=self.apply_filters_and_sort)
        self.sort_dropdown.configure(command=self.apply_filters_and_sort)
        reset_filters_button.configure(command=self.reset_filters)

    def refresh(self):
        """
        Refreshes the browsing frame to suit current filters
        """
        self.reset_filters()

    def reset_filters(self):
        """
        Resets all filters to their default value
        """
        # Turn off all checkboxes
        for checkbox in self.checkboxes.values():
            checkbox.deselect()
        # Turn off all radio buttons except the default (first)
        for count, radio_button in enumerate(self.radio_buttons):
            if count == 0:
                radio_button.select()
        # Turn off stock switch and reset the search bar / sort by dropdown
        self.stock_switch.select()
        self.sort_dropdown.reset()
        self.searchbar.reset_searchbar()
        # Apply default filters
        self.apply_filters_and_sort()

    def apply_filters_and_sort(self, _=None):
        """
        Applies the current filters and sorts and displays the associated products
        """
        # Start off with every product and eliminate those not required
        field_names = ["product_id",
                       "name",
                       "description",
                       "category",
                       "current_stock",
                       "sale_price",
                       "image_file",
                       "company_name",
                       "average_rating"]
        all_products = crud.search_joined_table("ecommerce",
                                                "Product",
                                                [["supplier",
                                                 "supplier_id"]],
                                                field_names,
                                                "")
        # If a search was entered into the search bar
        if self.searchbar.get_current_search() != "":
            # Only continue with products that match the search criteria
            searched_products = backend.search_products(all_products,
                                                        self.searchbar.get_current_search())
        else:
            # Reset searchbar to display placeholder text
            self.searchbar.reset_searchbar()
            # No products added or discarded
            searched_products = all_products
        # Apply all filters
        rating_boundary = self.radio_button_var.get()
        filtered_products = backend.filter_products(searched_products,
                                                    self.checkboxes,
                                                    int(rating_boundary[0]),
                                                    self.stock_switch_var.get())
        dropdown_value = self.sort_dropdown.get()
        if dropdown_value != "Default":
            field_name, direction = self.sort_categories.get(f"{dropdown_value}")
            if direction == "asc":
                is_desc = False
            else:
                is_desc = True
            # Sort the remaining products
            final_products = backend.sort_products_by(filtered_products, field_name, is_desc)
        else:
            final_products = filtered_products
        # Display the remaining products
        self.product_view.refresh_pockets(final_products)


class ProductComparisonFrame(cWidget.ParentFrame):
    """
    The screen that allows a customer to compare two products

    Parameters
    ----------
    app : any
        The main window of the application
    """
    def __init__(self, app):
        super().__init__(app,
                         fg_color="White")
        self.app = app
        self.grid_rowconfigure(0, weight=1, uniform="uniform")
        self.grid_rowconfigure(1, weight=4, uniform="uniform")
        self.grid_columnconfigure(0, weight=3, uniform="uniform")
        self.grid_columnconfigure(1, weight=3, uniform="uniform")
        self.grid_columnconfigure(2, weight=2, uniform="uniform")

        topbar = cWidget.Topbar(self, app)
        topbar.grid(row=0, column=0, columnspan=3, sticky="NSEW")

        # Frame to hold the two product frames
        self.pocket_frame = cWidget.Frame(self)
        self.pocket_frame.grid(row=1, column=0, columnspan=2, sticky="NSEW")
        self.pocket_frame.grid_propagate(False)
        self.pocket_frame.grid_rowconfigure(0, weight=1)
        self.pocket_frame.grid_columnconfigure(0, weight=1, uniform="uniform")
        self.pocket_frame.grid_columnconfigure(1, weight=1, uniform="uniform")

        button_frame = cWidget.Frame(self)
        button_frame.grid(row=1, column=2, sticky="SEW")
        button_frame.grid_columnconfigure(0, weight=1)
        add_new_products_button = cWidget.FilledButton(button_frame,
                                                       command=lambda: self.app.load_frame("BrowsingFrame"),
                                                       width=150,
                                                       bg_color="White",
                                                       font=("Inter Regular", 16),
                                                       text="Add new products")
        add_new_products_button.grid(row=0, column=0, pady=10, sticky="NSEW")
        download_comparison_button = cWidget.FilledButton(button_frame,
                                                          command=lambda: self.create_report("download"),
                                                          width=150,
                                                          bg_color="White",
                                                          font=("Inter Regular", 16),
                                                          text="Download comparison")
        download_comparison_button.grid(row=1, column=0, pady=10, sticky="NSEW")
        email_comparison_button = cWidget.FilledButton(button_frame,
                                                       command=lambda: self.create_report("email"),
                                                       width=150,
                                                       bg_color="White",
                                                       font=("Inter Regular", 16),
                                                       text="Email comparison")
        email_comparison_button.grid(row=2, column=0, pady=10, sticky="NSEW")
        delete_all_products_button = cWidget.FilledButton(button_frame,
                                                          width=150,
                                                          bg_color="White",
                                                          font=("Inter Regular", 16),
                                                          command=lambda: self.reset_compare_bucket(),
                                                          text="Delete all products")
        delete_all_products_button.grid(row=3, column=0, pady=10, sticky="NSEW")

    def refresh(self):
        """
        Updates the comparison screen to the most recent state
        """
        for widget in self.pocket_frame.winfo_children():
            widget.destroy()
        # Get the customer's current products that are being compared
        compare_bucket = self.app.get_current_user().get_compare_bucket()
        products_in_bucket = compare_bucket.get_products()
        for count in range(2):
            # If product number (count+1) is present and not null
            if len(products_in_bucket) >= count+1:
                # Display product
                product = products_in_bucket[count]

                outer_frame = cWidget.Frame(self.pocket_frame, border_width=1)
                outer_frame.grid_rowconfigure(0, weight=1)
                outer_frame.grid_columnconfigure(0, weight=1)
                outer_frame.grid(row=0, column=count, padx=10, pady=10, sticky="NSEW")

                product_slot = cWidget.ScrollableFrame(outer_frame)
                product_slot.grid_columnconfigure(0, weight=1)
                product_slot.grid(row=0, column=0, padx=3, pady=3, sticky="NSEW")

                # Top of frame (supplier + bin button)
                heading_frame = cWidget.Frame(product_slot)
                heading_frame.grid_columnconfigure(0, weight=2, uniform="uniform")
                heading_frame.grid_columnconfigure(1, weight=1, uniform="uniform")
                heading_frame.grid(row=0, column=0, padx=5, sticky="NSEW")

                supplier_label = cWidget.Label(heading_frame,
                                               font=("Inter Regular", 16),
                                               fg_color="White",
                                               text=product.get("company_name"))
                supplier_label.grid(row=0, column=0, pady=5, sticky="W")
                bin_button = cWidget.BlankButton(heading_frame,
                                                 command=lambda p=product: self.delete_product(p),
                                                 width=30,
                                                 height=40,
                                                 image_file="bin_icon.png",
                                                 image_width=25,
                                                 image_height=25)
                bin_button.grid(row=0, column=1, pady=5, sticky="E")

                body_frame = cWidget.Frame(product_slot)
                body_frame.grid(row=1, column=0, padx=5, sticky="NSEW")
                body_frame.grid_columnconfigure(0, weight=1)

                product_name_label = cWidget.Label(body_frame,
                                                   text=product.get("name"),
                                                   fg_color="White",
                                                   font=("Poppins Regular", 30),
                                                   max_line_length=15)
                product_name_label.grid(row=0, column=0, sticky="W")
                price = product.get("sale_price")
                price_label = cWidget.Label(body_frame,
                                            text=f"£{price:.2f}",
                                            fg_color="White",
                                            font=("Poppins Regular", 30))
                price_label.grid(row=1, column=0, sticky="W")
                product_image = cWidget.Label(body_frame,
                                              image_file=product.get("image_file"),
                                              image_width=100,
                                              image_height=100)
                product_image.grid(row=2, column=0)
                category = product.get("category")
                category_label = cWidget.Label(body_frame,
                                               font=("Inter Regular", 16),
                                               fg_color="White",
                                               text=f"Category: {category}")
                category_label.grid(row=3, column=0, sticky="W")
                rating = product.get("average_rating")
                rating_label = cWidget.Label(body_frame,
                                             text=rating,
                                             fg_color="White",
                                             font=("Inter Regular", 16),
                                             image_file="star_icon.png",
                                             image_width=15,
                                             image_height=15)
                rating_label.grid(row=4, column=0, sticky="W")
                description = backend.remove_redundant_whitespace(product.get("description"))
                description_label = cWidget.Label(body_frame,
                                                  text=description,
                                                  fg_color="White",
                                                  font=("Inter Regular", 16),
                                                  max_line_length=30)
                description_label.grid(row=5, column=0, sticky="W")
                add_to_basket_button = cWidget.FilledButton(body_frame,
                                                            command=lambda p=product: self.add_to_basket(p),
                                                            text="Add to basket",
                                                            font=("Inter Regular", 16),
                                                            height=35,
                                                            bg_color="White")
                add_to_basket_button.grid(row=6, column=0, pady=10)
            else:
                # Display an empty product slot
                empty_slot = cWidget.Frame(self.pocket_frame, border_width=1)
                empty_slot.grid(row=0, column=count, padx=10, pady=10, sticky="NSEW")
                empty_slot.grid_columnconfigure(0, weight=1)
                empty_slot.grid_rowconfigure(0, weight=1, uniform="uniform")
                empty_slot.grid_rowconfigure(1, weight=1, uniform="uniform")
                message_label = cWidget.Label(empty_slot,
                                              text=f"Slot {count+1} is empty.",
                                              fg_color="White",
                                              max_line_length=10,
                                              font=("Poppins Regular", 36))
                message_label.grid(row=0, column=0, sticky="S")
                add_product_button = cWidget.FilledButton(empty_slot,
                                                          text="Add a product",
                                                          bg_color=colours.get_bg_colour(),
                                                          command=lambda: self.app.load_frame("BrowsingFrame"))
                add_product_button.grid(row=1, column=0, sticky="N")

    def add_to_basket(self, product):
        """
        Add a product in the comparison bucket to the user's basket

        Parameters
        ----------
        product : dict
            The product to be added
        """
        basket = self.app.get_current_user().get_basket()
        in_basket = False
        # Check if the product is already in the basket
        for product in basket.get_products():
            if product.get("product_id") == product.get("product_id"):
                in_basket = True
                break
        if in_basket:
            mbox.showerror("Error!", "Item is already in your basket!")
        else:
            # Check the product is available
            if product.get("current_stock") == 0:
                mbox.showerror("Error!", "This product is currently unavailable!")
            else:
                product["quantity"] = 1
                basket.add(product)
                self.app.load_frame("BasketFrame")

    def delete_product(self, product):
        """
        Delete a product from the comparison bucket

        Parameters
        ----------
        product : dict
            The product to delete
        """
        compare_bucket = self.app.get_current_user().get_compare_bucket()
        compare_bucket.delete_product(product_id=product.get("product_id"))
        self.refresh()

    def reset_compare_bucket(self):
        """
        Resets the comparison bucket
        """
        compare_bucket = self.app.get_current_user().get_compare_bucket()
        compare_bucket.reset()
        self.refresh()

    def create_report(self, mode):
        """
        Calls upon the summary report manager to create a comparison report

        Parameters
        ----------
        mode : str
            The mode which determines how the report is stored, either 'download' or 'email'
        """
        compare_bucket = self.app.get_current_user().get_compare_bucket()
        # If the comparison bucket is full
        if compare_bucket.get_blanks() == 0:
            products = compare_bucket.get_products()
            summary_report_manager = self.app.expand_summary_report_manager()
            summary_report_manager.create_report(report_name="Product comparison",
                                                 mode=mode,
                                                 product_one=products[0],
                                                 product_two=products[1])
        else:
            mbox.showerror("Error!", f"Download unsuccessful!\n{compare_bucket.get_blanks()} product(s) have been left blank.")


class ProductFrame(cWidget.ParentFrame):
    """
    The screen that allows a customer to view a product in more detail

    Parameters
    ----------
    app : any
        The main window of the application
    """
    def __init__(self, app: any):
        super().__init__(app)
        self.app = app
        self.grid_rowconfigure(0, weight=1, uniform="uniform")
        self.grid_rowconfigure(1, weight=4, uniform="uniform")
        self.grid_columnconfigure(0, weight=1)

        topbar = cWidget.Topbar(self, app)
        topbar.grid(row=0, column=0, sticky="NSEW")

        self.body_frame = cWidget.ScrollableFrame(self)
        self.body_frame.grid(row=1, column=0, padx=2, sticky="NSEW")
        self.body_frame.grid_columnconfigure(0, weight=3, uniform="uniform")
        self.body_frame.grid_columnconfigure(1, weight=4, uniform="uniform")

    def refresh(self, product_details: dict):
        """
        Updates the product screen to its most recent state

        Parameters
        ----------
        product_details : dict
            The product data to display
        """
        for widget in self.body_frame.winfo_children():
            widget.destroy()

        # Output product data
        product_image = product_details.get("image_file")
        product_image_label = cWidget.Label(self.body_frame,
                                            image_file=f"{product_image}",
                                            image_width=300,
                                            image_height=300,
                                            fg_color="White")
        product_image_label.grid(row=0, column=0, pady=(20, 0), sticky="N")

        product_details_frame = cWidget.Frame(self.body_frame)
        product_details_frame.grid(row=0, column=1, pady=20, sticky="NEW")
        product_details_frame.grid_columnconfigure(0, weight=1)

        output_frame = cWidget.Frame(product_details_frame)
        output_frame.grid(row=0, column=0, sticky="NEW")
        output_frame.grid_columnconfigure(0, weight=1)

        supplier_name_label = cWidget.Label(output_frame,
                                            text=product_details.get("company_name"),
                                            fg_color="White",
                                            anchor="w")
        supplier_name_label.grid(row=0, column=0, padx=10, sticky="W")

        name_label = cWidget.Label(output_frame,
                                   text=product_details.get("name"),
                                   font=("Poppins Regular", 36),
                                   fg_color="White",
                                   anchor="w")
        name_label.grid(row=1, column=0, padx=10, sticky="SW")

        price_label = cWidget.Label(output_frame,
                                    text=f"£{product_details.get('sale_price'):.2f}",
                                    font=("Poppins Regular", 36),
                                    fg_color="White",
                                    anchor="w")
        price_label.grid(row=2, column=0, padx=10, pady=5, sticky="NW")

        rating_bar = cWidget.RatingBar(output_frame,
                                       app=self.app,
                                       product_id=product_details.get("product_id"))
        rating_bar.grid(row=3, column=0, padx=10, sticky="W")

        description = backend.remove_redundant_whitespace(product_details.get("description"))
        description_label = cWidget.Label(output_frame,
                                          text=description,
                                          max_line_length=50,
                                          fg_color="White",
                                          justify="left")
        description_label.grid(row=4, column=0, padx=10, sticky="W")

        input_frame = cWidget.Frame(product_details_frame)
        input_frame.grid(row=1, column=0, pady=(10, 0), sticky="NEW")
        input_frame.grid_columnconfigure(0, weight=1)
        
        def add_to_basket():
            """
            Adds a product to the basket
            """
            basket = self.app.get_current_user().get_basket()
            in_basket = False

            # Refuse process if the item already exists in the basket
            for product in basket.get_products():
                if product.get("product_id") == product_details.get("product_id"):
                    in_basket = True
                    break

            if in_basket:
                mbox.showerror("Error!", "Item is already in your basket!")
            else:
                product_details["quantity"] = quantity_tracker.get_count()
                basket.add(product_details)

                self.app.load_frame("BasketFrame")

        # Do not give the user the option to add to the basket if the product has no stock
        if product_details.get("current_stock") == 0:
            not_available_label = cWidget.Label(input_frame,
                                                text="Product is currently unavailable!",
                                                fg_color="White")
            not_available_label.grid(row=0, column=0, padx=10, sticky="SW")
        else:
            # If the current stock is less than the maximum product limit
            if product_details.get("current_stock") < 10:
                # Make the current stock the maximum product limit instead
                stock_maximum = product_details.get("current_stock")
            else:
                stock_maximum = 10
            quantity_tracker = cWidget.Counter(input_frame,
                                               style="+-",
                                               minimum=1,
                                               maximum=stock_maximum)
            quantity_tracker.grid(row=0, column=0, padx=10, sticky="SW")
            # Only display add to basket button if the stock > 0
            basket_button = cWidget.FilledButton(input_frame,
                                                 text="Add to basket",
                                                 command=add_to_basket,
                                                 bg_color="White")
            basket_button.grid(row=1, column=0, padx=10, pady=(10, 0), sticky="W")


class BasketFrame(cWidget.ParentFrame):
    """
    The screen that displays the basket and associated costs

    Parameters
    ----------
    app : any
        The main window of the application
    """
    def __init__(self, app: any):
        super().__init__(app)
        self.app = app
        self.grid_rowconfigure(0, weight=4, uniform="uniform")
        self.grid_rowconfigure(1, weight=1, uniform="uniform")
        self.grid_rowconfigure(2, weight=7, uniform="uniform")
        self.grid_rowconfigure(3, weight=7, uniform="uniform")
        self.grid_rowconfigure(4, weight=1, uniform="uniform")
        self.grid_columnconfigure(0, weight=11, uniform="uniform")
        self.grid_columnconfigure(1, weight=4, uniform="uniform")

        # Top-bar
        topbar = cWidget.Topbar(self, app, "Your basket")
        topbar.grid(row=0, column=0, columnspan=2, sticky="NSEW")

        # Initialise empty basket frame
        self.basket = None
        self.basket_frame = cWidget.Basket(self, app)
        self.basket_frame.grid(row=2, column=0, rowspan=2, padx=10,  sticky="NSEW")

        # Initialise empty cost frame
        self.costs_frame = cWidget.CostsFrame(self,
                                              continue_action=lambda: self.app.load_frame("CheckoutFrame"),
                                              back_action=lambda: self.app.load_frame("BrowsingFrame"))
        self.costs_frame.grid(row=2, column=1, padx=10, rowspan=2, sticky="NEW")

        # Initialise no basket message
        self.info_frame = cWidget.Frame(self)
        self.info_frame.grid(row=2, column=0, rowspan=2, columnspan=3, sticky="NSEW")
        self.info_frame.grid_rowconfigure(0, weight=1, uniform="uniform")
        self.info_frame.grid_rowconfigure(1, weight=1, uniform="uniform")
        self.info_frame.grid_columnconfigure(0, weight=1, uniform="uniform")
        no_basket_message = cWidget.Label(self.info_frame,
                                          text="There are currently no items in your basket")
        no_basket_message.grid(row=0, column=0, pady=5, sticky="S")
        continue_shopping_button = cWidget.FilledButton(self.info_frame,
                                                        text="Continue shopping",
                                                        bg_color="White",
                                                        command=lambda: self.app.load_frame("BrowsingFrame"))
        continue_shopping_button.grid(row=1, column=0, pady=5, sticky="N")
        # Hide empty basket message
        self.info_frame.grid_forget()

    def refresh_cost_frame(self):
        # Update stored totals in the actual basket
        self.basket.update_subtotal()
        # Update on-screen totals
        self.costs_frame.update_totals()

    def refresh_basket_and_costs(self, bin_product=None):
        """
        Method used to refresh the current basket and costs associated

        Parameters
        ----------
        bin_product : dict
            A dictionary of the product attributes of the item to delete.
            Keys should state the attribute names.
            Values should state the attributes themselves.
        """
        if bin_product:
            self.basket.delete_product(bin_product)
        # If a basket exists and has products in it
        if self.basket and self.basket.get_products():
            if self.info_frame.winfo_ismapped():
                self.info_frame.grid_forget()
                self.basket_frame.grid(row=2, column=0, rowspan=2, padx=10,  sticky="NSEW")
            # Update on-screen basket
            self.basket_frame.refresh()
            self.refresh_cost_frame()
        else:
            if not self.info_frame.winfo_ismapped():
                self.basket_frame.grid_forget()
                self.info_frame.grid(row=2, column=0, rowspan=2, columnspan=3, sticky="NSEW")

    def refresh(self):
        """
        Updates the basket screen to its most recent state
        """
        self.basket = self.app.get_current_user().get_basket()
        # Link current basket to the basket and costs display
        self.costs_frame.link_basket(self.basket)
        self.refresh_basket_and_costs()


class CheckoutFrame(cWidget.ParentFrame):
    """
    The screen that displays the basket and associated costs

    Parameters
    ----------
    app : any
        The main window of the application
    """
    def __init__(self, app: any):
        super().__init__(app)
        self.app = app
        self.matched_cards = []
        self.current_user = None

        self.grid_rowconfigure(0, weight=4, uniform="uniform")
        self.grid_rowconfigure(1, weight=1, uniform="uniform")
        self.grid_rowconfigure(2, weight=7, uniform="uniform")
        self.grid_rowconfigure(3, weight=7, uniform="uniform")
        self.grid_rowconfigure(4, weight=1, uniform="uniform")
        self.grid_columnconfigure(0, weight=7, uniform="uniform")
        self.grid_columnconfigure(1, weight=4, uniform="uniform")
        self.grid_columnconfigure(2, weight=4, uniform="uniform")
        self.grid_propagate(False)

        # Top-bar
        topbar = cWidget.Topbar(self, app, "Your basket")
        topbar.grid(row=0, column=0, columnspan=3, sticky="NSEW")

        outer_frame = cWidget.Frame(self,
                                    border_width=1)
        outer_frame.grid(row=2, column=0, rowspan=2, padx=(10, 0), sticky="NSEW")
        outer_frame.grid_rowconfigure(0, weight=1)
        outer_frame.grid_columnconfigure(0, weight=1)

        # Payment information
        self.existing_card_frame = cWidget.Frame(outer_frame)
        self.existing_card_frame.grid_columnconfigure(0, weight=2, uniform="uniform")
        self.existing_card_frame.grid_columnconfigure(1, weight=3, uniform="uniform")

        payment_heading = cWidget.Label(self.existing_card_frame,
                                        text="Your payment method",
                                        font=("Poppins Regular", 24),
                                        fg_color="White",
                                        anchor="w")
        payment_heading.grid(row=0, column=0, padx=10, pady=(10, 0), columnspan=2, sticky="EW")

        card_icon = cWidget.Label(self.existing_card_frame,
                                  image_file="card_icon.png",
                                  image_width=70,
                                  image_height=70,
                                  fg_color="White")
        card_icon.grid(row=1, column=0, padx=10, pady=(10, 0), sticky="NSEW")

        dropdown_frame = cWidget.Frame(self.existing_card_frame,
                                       border_width=1)
        dropdown_frame.grid(row=1, column=1, padx=10, pady=(10, 0), sticky="EW")
        dropdown_frame.grid_rowconfigure(0, weight=1)
        dropdown_frame.grid_columnconfigure(0, weight=1)
        # Initialise default card dropdown that shows existing cards
        self.card_dropdown = cWidget.Dropdown(dropdown_frame,
                                              values=[""],
                                              var_default="")
        self.card_dropdown.grid(row=0, column=0, padx=2, pady=2, sticky="NSEW")

        add_new_card_button = cWidget.FilledButton(self.existing_card_frame,
                                                   text="Add new card",
                                                   bg_color="White",
                                                   command=self.switch_to_new)
        add_new_card_button.grid(row=2, column=1, padx=10, pady=10, sticky="EW")

        self.new_card_frame = cWidget.ScrollableFrame(outer_frame)
        self.new_card_frame.grid(row=0, column=0, padx=2, pady=2, sticky="NSEW")
        self.new_card_frame.grid_columnconfigure(0, weight=1, uniform="uniform")
        self.new_card_frame.grid_columnconfigure(1, weight=1, uniform="uniform")
        self.new_card_frame.propagate(False)

        payment_heading = cWidget.Label(self.new_card_frame,
                                        text="Your payment method",
                                        font=("Poppins Regular", 24),
                                        fg_color="White",
                                        anchor="w")
        payment_heading.grid(row=0, column=0, padx=10, pady=(10, 0), columnspan=2, sticky="EW")

        # Row that user input widgets begin at
        count = 1

        card_num_label = cWidget.Label(self.new_card_frame,
                                       text="Card number:",
                                       fg_color="White",
                                       anchor="w")
        card_num_label.grid(row=count, column=0, padx=10, pady=(10, 0), columnspan=2, sticky="NSEW")
        card_num_entry = cWidget.Entry(self.new_card_frame, table_name="Payment_Card", field_name="card_number")
        card_num_entry.grid(row=count+1, column=0, columnspan=2, padx=10, sticky="NEW")

        expiry_date_label = cWidget.Label(self.new_card_frame,
                                          text="Expiry date:",
                                          fg_color="White",
                                          anchor="w")
        expiry_date_label.grid(row=count+2, column=0, padx=10, pady=(10, 0), sticky="NSEW")
        expiry_date_entry = cWidget.Entry(self.new_card_frame, table_name="Payment_Card", field_name="expiry_date")
        expiry_date_entry.grid(row=count+3, column=0, padx=10, sticky="NEW")

        cvc_label = cWidget.Label(self.new_card_frame,
                                  text="CVC:",
                                  fg_color="White")
        cvc_label.grid(row=count+2, column=1, padx=10, pady=(10, 0), sticky="NSEW")
        cvc_entry = cWidget.Entry(self.new_card_frame, table_name="Payment_Card", field_name="cvc")
        cvc_entry.grid(row=count+3, column=1, padx=10, sticky="NEW")

        holder_name_label = cWidget.Label(self.new_card_frame,
                                          text="Cardholder name:",
                                          fg_color="White",
                                          anchor="w")
        holder_name_label.grid(row=count+4, column=0, padx=10, pady=(10, 0), columnspan=2, sticky="NSEW")
        holder_name_entry = cWidget.Entry(self.new_card_frame, table_name="Payment_Card", field_name="cardholder_name")
        holder_name_entry.grid(row=count+5, column=0, columnspan=2, padx=10, sticky="NEW")

        billing_address_label = cWidget.Label(self.new_card_frame,
                                              text="Billing address:",
                                              fg_color="White",
                                              anchor="w")
        billing_address_label.grid(row=count+6, column=0, padx=10, pady=(10, 0), columnspan=2, sticky="NSEW")
        billing_address_entry = cWidget.Entry(self.new_card_frame, table_name="Payment_Card", field_name="billing_address")
        billing_address_entry.grid(row=count+7, column=0, columnspan=2, padx=10, sticky="NEW")

        billing_postcode_label = cWidget.Label(self.new_card_frame,
                                               text="Billing postcode:",
                                               fg_color="White",
                                               anchor="w")
        billing_postcode_label.grid(row=count+8, column=0, padx=10, pady=(10, 0), columnspan=2, sticky="NSEW")
        billing_postcode_entry = cWidget.Entry(self.new_card_frame, table_name="Payment_Card", field_name="billing_postcode")
        billing_postcode_entry.grid(row=count+9, column=0, columnspan=2, padx=10, sticky="NEW")

        self.card_entry_widgets = {"card_number": card_num_entry,
                                   "cvc": cvc_entry,
                                   "expiry_date": expiry_date_entry,
                                   "cardholder_name": holder_name_entry,
                                   "billing_address": billing_address_entry,
                                   "billing_postcode": billing_postcode_entry}

        clear_button = cWidget.FilledButton(self.new_card_frame,
                                            text="Clear input",
                                            bg_color="White",
                                            command=lambda: backend.clear_entry_widgets(list(self.card_entry_widgets.values())))
        clear_button.grid(row=count+10, column=0, padx=(10, 5), pady=10, sticky="EW")

        use_existing_button = cWidget.FilledButton(self.new_card_frame,
                                                   text="Use existing card",
                                                   bg_color="White",
                                                   command=self.switch_to_existing,
                                                   font=("Inter Regular", 16))
        use_existing_button.grid(row=count+10, column=1, padx=(5, 10), pady=10, sticky="EW")

        # Delivery information
        delivery_frame = cWidget.Frame(self, border_width=1)
        delivery_frame.grid(row=2, column=1, padx=(10, 0), rowspan=2, sticky="NSEW")
        delivery_frame.grid_columnconfigure(0, weight=1)

        delivery_heading = cWidget.Label(delivery_frame,
                                         text="Your delivery information",
                                         font=("Poppins Regular", 24),
                                         justify="left",
                                         max_line_length=14,
                                         fg_color="White",
                                         anchor="w")
        delivery_heading.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="EW")

        delivery_fields = ["delivery_address",
                           "delivery_postcode"]
        self.delivery_entry_widgets = {}

        del_row = 1
        # Place all delivery information widgets
        for count, field_name in enumerate(delivery_fields):
            new_label = cWidget.Label(delivery_frame,
                                      text=f"{backend.convert_field_name_style(field_name)}",
                                      fg_color="White",
                                      anchor="w")
            new_entry = cWidget.Entry(delivery_frame, table_name="Orders", field_name=field_name)
            new_label.grid(row=del_row, column=0, padx=10, pady=(10, 0), sticky="EW")
            new_entry.grid(row=del_row+1, column=0, padx=10, sticky="EW")
            self.delivery_entry_widgets[delivery_fields[count]] = new_entry
            del_row += 2

        delivery_clear_button = cWidget.FilledButton(delivery_frame,
                                                     text="Clear input",
                                                     command=lambda: backend.clear_entry_widgets(list(self.delivery_entry_widgets.values())),
                                                     bg_color="White")
        delivery_clear_button.grid(row=del_row, column=0, padx=10, pady=10, sticky="NSEW")

        def validate_inputs():
            """
            Validates payment and delivery input
            """
            customer_id = self.app.get_current_user().get_personal_id()
            new_card_created = False
            # If a new card needs to be validated
            if self.new_card_frame.winfo_ismapped():
                card_info = {field_name: entry_widget.get()
                             for field_name, entry_widget in self.card_entry_widgets.items()}
                card_validity = [entry_widget.check_if_valid() for entry_widget in self.card_entry_widgets.values()]
                # Add customer ID to new card
                card_info["customer_id"] = customer_id
                new_card_created = True
            else:
                # Get the already validated card details from the existing card
                card_info = self.matched_cards[self.card_dropdown.get()]
                card_validity = [True] * len(card_info)

            delivery_info = {field_name: entry_widget.get()
                             for field_name, entry_widget in self.delivery_entry_widgets.items()}
            delivery_validity = [entry_widget.check_if_valid() for entry_widget in self.delivery_entry_widgets.values()]

            if False in card_validity or False in delivery_validity:
                mbox.showerror("Error!", "Invalid input")
            else:
                self.app.load_frame("ProcessingOrderFrame",
                                    card_info=card_info,
                                    new_card_created=new_card_created,
                                    delivery_info=delivery_info)

        self.costs_frame = cWidget.CostsFrame(self,
                                              continue_message="Confirm purchase",
                                              back_action=lambda: self.app.load_frame("BrowsingFrame"),
                                              continue_action=validate_inputs)
        self.costs_frame.grid(row=2, column=2, padx=10, rowspan=2, sticky="NEW")

    def switch_to_existing(self):
        """
        Switches from creating a new card to using an existing card
        """
        # Checks for user to prevent crash upon initialisation
        if self.current_user:
            # If the user has existing cards
            if self.matched_cards:
                dropdown_values = list(self.matched_cards.keys())
                self.card_dropdown.configure(values=dropdown_values)
                self.card_dropdown.set_default(dropdown_values[0])
                self.new_card_frame.grid_forget()
                self.existing_card_frame.grid(row=0, column=0, padx=2, pady=2, sticky="NSEW")
            else:
                mbox.showerror("Error!", "You have no existing payment methods")

    def switch_to_new(self):
        """
        Switches from using an existing card to creating a new card
        """
        # If new card is not already mapped
        if self.existing_card_frame.winfo_ismapped():
            self.existing_card_frame.grid_forget()
            self.new_card_frame.grid(row=0, column=0, padx=2, pady=2, sticky="NSEW")

    def refresh(self):
        """
        Updates the checkout screen to its most recent state
        """
        self.current_user = self.app.get_current_user()
        # Clear entry widgets
        backend.clear_entry_widgets(list(self.delivery_entry_widgets.values()))
        if self.new_card_frame.winfo_ismapped():
            backend.clear_entry_widgets(list(self.card_entry_widgets.values()))
        # Configure card output
        card_search = crud.search_table("ecommerce",
                                        "Payment_Card",
                                        ["*"],
                                        f"customer_id = '{self.current_user.get_personal_id()}'")
        # Get existing cards
        self.matched_cards = {f"ends in {card.get('card_number')[-4:]}": card for card in card_search}
        print(self.matched_cards)
        if self.matched_cards:
            self.switch_to_existing()
        else:
            self.switch_to_new()
        # Update cost outputs
        self.costs_frame.link_basket(self.current_user.get_basket())
        self.costs_frame.update_totals()


class ConfirmationFrame(cWidget.ParentFrame):
    """
    The screen that displays an order confirmation

    Parameters
    ----------
    app : any
        The main window of the application
    """
    def __init__(self, app: any):
        super().__init__(app, fg_color=colours.get_primary_colour())
        self.app = app
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        content_frame = tk.Frame(self,
                                 bg=colours.get_primary_colour())
        content_frame.grid(row=0,
                           column=0)

        thank_you_text = cWidget.Label(content_frame,
                                       text="Thank you for your order!",
                                       font=("Poppins Regular", 48),
                                       fg_color=colours.get_primary_colour())
        thank_you_text.pack()

        # Initialise default order id label
        self.order_id_text = cWidget.Label(content_frame,
                                           text=f"Your order ID: N/A",
                                           fg_color=colours.get_primary_colour())
        self.order_id_text.pack()

        tick_image = cWidget.Label(content_frame,
                                   image_file="tick_icon.png",
                                   image_width=150,
                                   image_height=150,
                                   fg_color=colours.get_primary_colour())
        tick_image.pack(pady=10)

        self.email_text = cWidget.Label(content_frame,
                                        text="",
                                        fg_color=colours.get_primary_colour())
        self.email_text.pack()

        paragraph_text = cWidget.Label(content_frame,
                                       text="You can check the status of any orders in the 'My orders' section of your profile.",
                                       max_line_length=50,
                                       justify="center",
                                       fg_color=colours.get_primary_colour())
        paragraph_text.pack(pady=(5, 0))

        home_button = cWidget.FilledButton(content_frame,
                                           text="Back to home",
                                           command=lambda: self.app.load_frame("BrowsingFrame"))
        home_button.pack(pady=30)

    def refresh(self, order_id: int, email_was_successful: bool = False):
        """
        Updates the confirmation screen for the order most recently processes

        Parameters
        ----------
        order_id : int
            The ID of the order just processed

        email_was_successful : bool
            Whether the order receipt was sent via email, either True if sent or False if not
        """
        self.order_id_text.configure(text=f"Your order ID: {order_id}")
        if email_was_successful:
            self.email_text.configure(text="An order confirmation has been sent to your email!")


class MyProfileFrame(cWidget.ParentFrame):
    """
    The screen that displays the user's profile and allows it to be edited

    Parameters
    ----------
    app : any
        The main window of the application
    """
    def __init__(self, app: any):
        super().__init__(app,
                         fg_color="White")
        self.app = app
        self.grid_rowconfigure(0, weight=4, uniform="uniform")
        self.grid_rowconfigure(1, weight=16, uniform="uniform")
        self.grid_columnconfigure(0, weight=4, uniform="uniform")
        self.grid_columnconfigure(1, weight=2, uniform="uniform")

        # Top-bar
        topbar = cWidget.Topbar(self, app, "My profile")
        topbar.grid(row=0, column=0, columnspan=2, sticky="NSEW")

        outer_frame = cWidget.Frame(self, border_width=1)
        outer_frame.grid(row=1, column=0, pady=20, padx=(75, 40), sticky="NSEW")
        outer_frame.grid_rowconfigure(0, weight=1)
        outer_frame.grid_columnconfigure(0, weight=1)
        self.account_details_frame = cWidget.ScrollableFrame(outer_frame)
        self.account_details_frame.grid(row=0, column=0, pady=2, padx=2, sticky="NSEW")
        self.account_details_frame.grid_columnconfigure(0, weight=1)
        self.entry_widgets = {}
        self.visibility_button = None

        button_frame = cWidget.Frame(self)
        button_frame.grid(row=1, column=1, padx=(0, 30), pady=20, sticky="SW")

        save_changes_button = cWidget.FilledButton(button_frame,
                                                   text="Save changes",
                                                   command=lambda: self.save_changes(),
                                                   bg_color="White")
        save_changes_button.pack(fill="x")

        clear_input_button = cWidget.FilledButton(button_frame,
                                                  text="Clear changes",
                                                  command=lambda: self.clear_changes(),
                                                  bg_color="White")
        clear_input_button.pack(fill="x", pady=(10, 0))

        delete_account_button = cWidget.FilledButton(button_frame,
                                                     text="Delete account",
                                                     command=lambda: self.delete_account(),
                                                     bg_color="White")
        delete_account_button.pack(fill="x", pady=(10, 0))

    def refresh(self):
        """
        Updates the profile screen to show the current user's profile
        """
        headings = ["Username:", "Password:", "Name:", "Surname:", "Email address:"]
        # Get details of user currently logged in
        current_details = crud.search_table("ecommerce",
                                            "Customer",
                                            ["*"],
                                            f"customer_id = {self.app.get_current_user().get_personal_id()}")[0]
        field_headings = crud.get_table_headings("ecommerce", "Customer")[1:]
        self.entry_widgets = {}

        for count, field in enumerate(headings):
            heading_row = count * 2
            heading_label = cWidget.Label(self.account_details_frame,
                                          fg_color="White",
                                          text=field)
            heading_label.grid(row=heading_row, column=0, padx=10, pady=(20, 0), sticky="W")
            # Enable password masking
            if field_headings[count] == "password":
                hideable = True
            else:
                hideable = False
            field_entry = cWidget.Entry(self.account_details_frame,
                                        table_name="Customer",
                                        field_name=field_headings[count],
                                        toggleable=True,
                                        current_text=current_details.get(field_headings[count]),
                                        hideable=hideable)
            field_entry.grid(row=heading_row + 1, column=0, padx=10,  columnspan=2, sticky="EW")
            self.entry_widgets[field_headings[count]] = field_entry

    def save_changes(self):
        """
        Save the changes made to the profile
        """
        current_details = crud.search_table("ecommerce",
                                            "Customer",
                                            ["*"],
                                            f"customer_id = {self.app.get_current_user().get_personal_id()}")[0]
        proposed_update_data = {}
        input_validities = []
        for field_name, entry_widget in self.entry_widgets.items():
            # For any attributes that have been altered
            if entry_widget.get() != current_details.get(field_name) and entry_widget.get() != "":
                input_validities.append(entry_widget.check_if_valid())
                # Add to list of update data
                proposed_update_data[field_name] = entry_widget.get()

        # If no attributes have changed
        if not proposed_update_data:
            self.refresh()
        else:
            if False not in input_validities:
                customer = self.app.get_current_user()
                customer_id = customer.get_personal_id()
                crud.update_record("ecommerce",
                                   "Customer",
                                   proposed_update_data,
                                   f"customer_id = {customer_id}")
                customer.refresh_details()
                self.refresh()
                mbox.showinfo("Success!", "Details successfully updated!")
            else:
                mbox.showerror("Error!", "Input invalid!")

    def clear_changes(self):
        """
        Clear any editing made
        """
        for entry_widget in self.entry_widgets.values():
            entry_widget.clear()

    def delete_account(self):
        """
        Deletes a customer's account
        """
        # Warns the user of the consequences
        delete_confirmed = mbox.askyesnocancel("Warning!", """This action is PERMANENT and will DELETE ALL OF YOUR
DETAILS, CARDS, ORDERS and RATINGS.\nAre you sure you want to continue?""")
        if delete_confirmed:
            customer = self.app.get_current_user()
            customer_id = customer.get_personal_id()
            # For all pending orders deleted, refund the stock
            orders_pending = crud.search_table("ecommerce",
                                               "Orders",
                                               ["*"],
                                               f"customer_id = '{customer_id}' AND delivery_status = 'Pending'")
            products_per_order = []
            for order in orders_pending:
                products_bought = crud.search_table("ecommerce",
                                                    "Order_Product",
                                                    ["*"],
                                                    f"order_id = '{order.get('order_id')}'")
                products_per_order.append(products_bought)
                for product in products_bought:
                    backend.decrease_stock_by(product.get("product_id"), -(product.get("quantity")))

            ratings_to_delete = crud.search_table("ecommerce", "Ratings", "*", f"customer_id = '{customer_id}'")

            # Delete record and all linked records
            crud.delete_record("ecommerce",
                               "Customer",
                               f"customer_id = {customer_id}")

            # For all ratings deleted, update average rating
            for rating in ratings_to_delete:
                backend.update_product_rating(rating.get("product_id"))

            # For all pending orders deleted, decrease the total sold
            for products_bought in products_per_order:
                for product in products_bought:
                    backend.update_total_sold(product.get("product_id"))
            # Returns to the home screen
            self.app.logout()


class MyCardsFrame(cWidget.ParentFrame):
    """
    The screen that displays the user's cards and allows them to be created / edited

    Parameters
    ----------
    app : any
        The main window of the application
    """
    def __init__(self, app: any):
        super().__init__(app,
                         fg_color="White")
        self.app = app
        self.grid_rowconfigure(0, weight=4, uniform="uniform")
        self.grid_rowconfigure(1, weight=16, uniform="uniform")
        self.grid_columnconfigure(0, weight=1)

        # Top-bar
        topbar = cWidget.Topbar(self, app, "My cards")
        topbar.grid(row=0, column=0, sticky="NSEW")

        # Body of window
        body_frame = cWidget.Frame(self, border_width=1)
        body_frame.grid(row=1, column=0, padx=20, pady=10, sticky="NSEW")
        body_frame.grid_rowconfigure(0, weight=1)
        body_frame.grid_columnconfigure(0, weight=20, uniform="uniform")
        body_frame.grid_columnconfigure(1, weight=1, uniform="uniform")
        body_frame.grid_columnconfigure(2, weight=10, uniform="uniform")

        # If a card exists, display this frame
        self.card_frame = cWidget.Frame(body_frame)
        self.card_frame.grid(row=0, column=0, padx=2, pady=2, sticky="NSEW")
        self.card_frame.grid_rowconfigure(0, weight=1)
        self.card_frame.grid_columnconfigure(0, weight=1)
        self.inner_frame = cWidget.ScrollableFrame(self.card_frame)
        self.inner_frame.grid(row=0, column=0, padx=2, pady=2, sticky="NSEW")
        self.inner_frame.grid_columnconfigure(0, weight=1, uniform="uniform")
        self.inner_frame.grid_columnconfigure(1, weight=1, uniform="uniform")

        vertical_separator = ttk.Separator(body_frame, orient="vertical")
        sep_style = ttk.Style(vertical_separator)
        sep_style.configure('TSeparator', background="Black")
        vertical_separator.grid(row=0, column=1, sticky="NS")

        # Action frame
        self.action_frame = cWidget.Frame(body_frame)
        self.action_frame.grid(row=0, column=2, sticky="NSEW", padx=15, pady=2)
        self.action_frame.grid_columnconfigure(0, weight=1)

        card_image = cWidget.Label(self.action_frame,
                                   image_file="card_icon.png",
                                   image_width=160,
                                   image_height=125,
                                   fg_color="White")
        card_image.grid(row=0, column=0, pady=(10, 0))

        # Place card dropdown menu into details frame
        self.dropdown_frame = cWidget.Frame(self.action_frame, border_width=1)
        self.dropdown_frame.grid(row=1, column=0, padx=10, pady=(10, 0), sticky="EW")
        self.dropdown_frame.grid_rowconfigure(0, weight=1)
        self.dropdown_frame.grid_columnconfigure(0, weight=1)
        self.card_dropdown = cWidget.Dropdown(self.dropdown_frame,
                                              command=self.change_card,
                                              values=[""],
                                              var_default="")

        self.save_changes_button = cWidget.FilledButton(self.action_frame,
                                                        command=None,
                                                        text="Save changes",
                                                        bg_color="White")
        self.save_changes_button.grid(row=2, column=0, padx=10, pady=(10, 0), sticky="EW")

        clear_input_button = cWidget.FilledButton(self.action_frame,
                                                  command=lambda: self.clear_changes(),
                                                  text="Clear changes",
                                                  bg_color="White")
        clear_input_button.grid(row=3, column=0, padx=10, pady=(10, 0), sticky="EW")

        self.switch_mode_button = cWidget.FilledButton(self.action_frame, bg_color="White")
        self.switch_mode_button.grid(row=4, column=0, padx=10, pady=(10, 0), sticky="EW")

        self.delete_card_button = cWidget.FilledButton(self.action_frame,
                                                       command=lambda: self.delete_card(),
                                                       text="Delete card",
                                                       bg_color="White")

        self.entry_widgets = {}
        self.dropdown_values = {}

    def refresh(self):
        """
        Updates the cards screen to the most recent state
        """
        self.switch_to_existing()

    def switch_to_existing(self):
        """
        Switches from creating a new card to viewing an existing one
        """
        all_cards = crud.search_table("ecommerce",
                                      "Payment_Card",
                                      ["*"],
                                      f"customer_id = '{self.app.get_current_user().get_personal_id()}'")
        self.dropdown_values = {card.get("card_number"): card for card in all_cards}
        # If cards exist
        if self.dropdown_values:
            self.dropdown_frame.configure(border_width=1)
            self.card_dropdown.grid(row=0, column=0, padx=1, pady=1, sticky="NSEW")
            self.delete_card_button.grid(row=5, column=0, padx=10, pady=(10, 0), sticky="EW")
            self.save_changes_button.configure(text="Save changes", command=lambda: self.update_card())
            self.switch_mode_button.configure(text="Create a new card", command=lambda: self.switch_to_new())
            # Configure card dropdown
            self.card_dropdown.configure(values=list(self.dropdown_values.keys()))
            self.card_dropdown.set_default(list(self.dropdown_values.keys())[0])
            self.card_dropdown.set(list(self.dropdown_values.keys())[0])
            self.change_card(self.card_dropdown.get())
        else:
            self.switch_to_new()
        mbox.showinfo("Info!", f"You currently have {len(self.dropdown_values)} card(s)!")

    def switch_to_new(self):
        """
        Switches from to viewing an existing card to creating a new one
        """
        self.dropdown_frame.configure(border_width=0)
        self.card_dropdown.grid_forget()
        self.delete_card_button.grid_forget()
        self.save_changes_button.configure(text="Create card", command=lambda: self.create_new_card())
        self.switch_mode_button.configure(text="Change existing card", command=lambda: self.switch_to_existing())
        self.change_card()

    def change_card(self, card_number: str = None):
        """
        Changes the existing card currently in focus

        Parameters
        ----------
        last_four_digits : str
            The last four digits of the card number for the card
        """
        for widget in self.inner_frame.winfo_children():
            widget.destroy()

        headings = ["Card number", "CVC", "Expiry date", "Cardholder name", "Billing address", "Billing postcode"]
        field_headings = crud.get_table_headings("ecommerce", "Payment_Card")[1:]
        self.entry_widgets = {}

        if card_number:
            card = self.dropdown_values.get(card_number)

        for count, field in enumerate(headings):
            heading_label = cWidget.Label(self.inner_frame,
                                          fg_color="White",
                                          text=field)
            # Define special case where two field inputs are on one line
            if field != "Expiry date" and field != "CVC":
                heading_row = count * 2
                column = 0
                column_span = 2
            else:
                heading_row = 2
                # Define special case where expiry date input is on the right column
                if field == "Expiry date":
                    column = 1
                else:
                    column = 0
                column_span = 1
            heading_label.grid(row=heading_row,
                               column=column,
                               padx=10,
                               pady=(19, 0),
                               columnspan=column_span,
                               sticky="W")

            # Define fields which can be masked
            if (
                    field_headings[count] == "card_number"
                    or field_headings[count] == "cvc"
                    or field_headings[count] == "expiry_date"
            ):
                hideable = True
            else:
                hideable = False

            if card_number:
                field_entry = cWidget.Entry(self.inner_frame,
                                            table_name="Payment_Card",
                                            field_name=field_headings[count],
                                            toggleable=True,
                                            current_text=card.get(field_headings[count]),
                                            hideable=hideable)
            else:
                # If no card is in focus, the user is creating one
                # Define entry widget to only create input
                field_entry = cWidget.Entry(self.inner_frame,
                                            table_name="Payment_Card",
                                            field_name=field_headings[count])
            field_entry.grid(row=heading_row+1,
                             column=column,
                             padx=10,
                             columnspan=column_span,
                             sticky="EW")
            self.entry_widgets[field_headings[count]] = field_entry

    def create_new_card(self):
        """
        Create a new payment card
        """
        card_input = {field_name: card_entry.get() for field_name, card_entry in self.entry_widgets.items()}
        input_validities = [entry.check_if_valid() for entry in self.entry_widgets.values()]
        if False not in input_validities:
            card_input["customer_id"] = self.app.get_current_user().get_personal_id()
            crud.add_record("ecommerce", "Payment_Card", card_input)
            self.refresh()
            mbox.showinfo("Success!", "Your card was successfully created!")
        else:
            mbox.showerror("Error!", "Input invalid.")

    def update_card(self):
        """
        Update an existing card
        """
        card_to_update = self.dropdown_values.get(self.card_dropdown.get())
        input_validities = []
        proposed_update_data = {}
        for field_name, entry_widget in self.entry_widgets.items():
            if entry_widget.get() != card_to_update.get(field_name) and entry_widget.get() != "":
                proposed_update_data[field_name] = entry_widget.get()
                input_validities.append(entry_widget.check_if_valid())

        # If no attributes have been changed
        if not proposed_update_data:
            self.refresh()
        else:
            if False not in input_validities:
                search_criteria = backend.encrypt("card_number", card_to_update.get('card_number'))
                crud.update_record("ecommerce",
                                   "Payment_Card",
                                   proposed_update_data,
                                   f"card_number = '{search_criteria}'")
                self.refresh()
                mbox.showinfo("Success!", "Card successfully updated!")
            else:
                mbox.showerror("Error!", "Invalid input.")

    def clear_changes(self):
        """
        Clear any edits made
        """
        for entry_widget in self.entry_widgets.values():
            entry_widget.clear()

    def delete_card(self):
        """
        Deletes a payment card from the database / system
        """
        # Warns the user of the consequence
        delete_confirmed = mbox.askyesnocancel("Warning!", """This action is PERMANENT and will DELETE ALL ORDERS LINKED
TO THAT CARD.\nAre you sure you want to continue?""")
        if delete_confirmed:
            card_to_delete = self.dropdown_values.get(self.card_dropdown.get())
            delete_id = card_to_delete.get("payment_card_id")
            # For all pending orders deleted, refund the stock
            orders_pending = crud.search_table("ecommerce",
                                               "Orders",
                                               ["*"],
                                               f"payment_card_id = '{delete_id}' AND delivery_status = 'Pending'")
            products_per_order = []
            for order in orders_pending:
                products_bought = crud.search_table("ecommerce",
                                                    "Order_Product",
                                                    ["*"],
                                                    f"order_id = '{order.get('order_id')}'")
                products_per_order.append(products_bought)
                for product in products_bought:
                    backend.decrease_stock_by(product.get("product_id"), -(product.get("quantity")))
            crud.delete_record("ecommerce",
                               "Payment_Card",
                               f"payment_card_id = '{delete_id}'")
            # For all pending orders deleted, decrease the total sold
            for products_bought in products_per_order:
                for product in products_bought:
                    backend.update_total_sold(product.get("product_id"))
            self.switch_to_existing()
            mbox.showinfo("Success!", "Card successfully deleted!")
            

class MyOrdersFrame(cWidget.ParentFrame):
    """
    The screen that displays the user's past orders

    Parameters
    ----------
    app : any
        The main window of the application
    """
    def __init__(self, app: any):
        super().__init__(app,
                         fg_color="White")
        self.app = app
        self.grid_rowconfigure(0, weight=4, uniform="uniform")
        self.grid_rowconfigure(1, weight=13, uniform="uniform")
        self.grid_rowconfigure(2, weight=3, uniform="uniform")
        self.grid_columnconfigure(0, weight=1)

        # Top-bar
        topbar = cWidget.Topbar(self, app, "My orders")
        topbar.grid(row=0, column=0, sticky="NSEW")

        self.slideshow_frame = cWidget.Frame(self)
        self.slideshow_frame.grid(row=1, column=0, sticky="NSEW")
        self.slideshow_frame.grid_rowconfigure(0, weight=1)
        self.slideshow_frame.grid_columnconfigure(0, weight=1)
        self.order_slideshow = None

        # Holds order pages (2 orders per page)
        self.paged_orders = []

        self.page_tracker = cWidget.PageTracker(self)
        self.page_tracker.grid(row=2, column=0, padx=15, sticky="E")

        self.info_frame = cWidget.Frame(self)
        self.info_frame.grid_rowconfigure(0, weight=1)
        self.info_frame.grid_rowconfigure(1, weight=1)
        self.info_frame.grid_columnconfigure(0, weight=1)

        no_orders_found = cWidget.Label(self.info_frame,
                                        text="No orders found!",
                                        fg_color="White")
        no_orders_found.grid(row=0, column=0, sticky="S")
        issue_resolution_label = cWidget.Label(self.info_frame,
                                               text="Expecting results? Get in touch with one of our support staff.",
                                               fg_color="White",
                                               anchor="center",
                                               max_line_length=200)
        issue_resolution_label.grid(row=1, column=0, sticky="N")

    def refresh(self):
        """
        """
        # Create slideshow and link page tracker to slideshow
        self.order_slideshow = cWidget.Slideshow(self.slideshow_frame,
                                                 width=self.slideshow_frame.winfo_width(),
                                                 height=self.slideshow_frame.winfo_height())
        self.order_slideshow.grid(row=0, column=0, sticky="NSEW")
        self.page_tracker.link_slideshow(self.order_slideshow)
        customer_id = self.app.get_current_user().get_personal_id()
        orders = crud.search_joined_table("ecommerce",
                                          "Orders",
                                          [["Payment_Card", "payment_card_id"]],
                                          ["*"],
                                          f"Orders.customer_id = '{customer_id}'")
        sorted_orders = sorted(orders, key=lambda sorted_order: sorted_order["date"], reverse=True)
        # Lifted from GeekForGeeks: https://www.geeksforgeeks.org/break-list-chunks-size-n-python/
        n = 2
        self.paged_orders = [sorted_orders[i * n:(i + 1) * n] for i in range((len(sorted_orders) + n - 1) // n)]
        # End of copied snippet

        # If there are orders
        if self.paged_orders:
            self.info_frame.grid_forget()
            self.slideshow_frame.grid(row=1, column=0, padx=15, sticky="NSEW")
            self.page_tracker.set_maximum(len(self.paged_orders))
            self.page_tracker.set_count(1)

            # Create page number 1 (first 2 orders)
            current_frame = self.create_page(1)
            self.order_slideshow.set_current_frame(current_frame)
            self.update_adjacent_pages()
        else:
            self.slideshow_frame.grid_forget()
            self.info_frame.grid(row=1, column=0, rowspan=2, sticky="NSEW")

    def update_adjacent_pages(self):
        """
        Set the next and previous pages of orders (if they exist)
        """
        # If there are still new order pages available
        if len(self.paged_orders) > self.page_tracker.get_count():
            self.page_tracker.set_next_page(self.create_page(self.page_tracker.get_count()+1))
        else:
            self.page_tracker.set_next_page(None)

        # If there are previous order pages available
        if self.page_tracker.get_count() != 1:
            self.page_tracker.set_previous_page(self.create_page(self.page_tracker.get_count()-1))
        else:
            self.page_tracker.set_previous_page(None)

    def create_page(self, page_num: int):
        """
        Creates a page of orders with 2 orders per page

        Parameters
        ----------
        page_num : int
            The number of the page

        Returns
        -------
        ctk.CTkFrame
            The order page
        """
        order_page = cWidget.Frame(self.order_slideshow)
        order_page.grid_rowconfigure(0, weight=1, uniform="hi")
        order_page.grid_rowconfigure(1, weight=1, uniform="hi")
        order_page.grid_columnconfigure(0, weight=1)
        for count, order in enumerate(self.paged_orders[page_num-1]):
            order_pocket = cWidget.Frame(order_page, border_width=1)
            order_pocket.grid(row=count, column=0, pady=10, sticky="NSEW")
            order_pocket.propagate(False)
            order_pocket.grid_rowconfigure(0, weight=1)
            order_pocket.grid_rowconfigure(1, weight=1)
            order_pocket.grid_rowconfigure(2, weight=1)
            order_pocket.grid_rowconfigure(3, weight=1)
            order_pocket.grid_columnconfigure(0, weight=1, uniform="uniform")
            order_pocket.grid_columnconfigure(1, weight=1, uniform="uniform")
            order_pocket.grid_columnconfigure(2, weight=1, uniform="uniform")
            order_pocket.grid_columnconfigure(3, weight=1, uniform="uniform")

            image_grid = cWidget.Frame(order_pocket)
            image_grid.grid(row=1, column=0, rowspan=2)
            image_grid.grid_rowconfigure(0, weight=1)
            image_grid.grid_rowconfigure(1, weight=1)
            image_grid.grid_columnconfigure(0, weight=2)
            image_grid.grid_columnconfigure(1, weight=1)

            order_id = order.get("order_id")
            products_bought = crud.search_joined_table("ecommerce",
                                                       "Order_Product",
                                                       [["Product", "product_id"]],
                                                       ["*"],
                                                       f"order_id = '{order_id}'")

            # If there are two or more images
            if len(products_bought) != 1:
                # Displays images as below (1 = image one and 2 = image two)
                # 1 1 1 1 2 2 
                # 1 1 1 1 2 2 
                # 1 1 1 1 - -
                # 1 1 1 1 - -
                for n in range(2):
                    image_file = products_bought[n].get("image_file")
                    image = cWidget.Label(image_grid,
                                          image_file=image_file,
                                          image_width=76 / (n + 1),
                                          image_height=76 / (n + 1),
                                          fg_color="White")
                    image.grid(row=0, column=n, rowspan=2 - n, sticky="NSEW")

                additional_undisplayed_images = len(products_bought) - 2
                # Display count of products not displayed in the two images
                undisplayed_image_count = cWidget.Label(image_grid,
                                                        text=f"+{additional_undisplayed_images}",
                                                        fg_color="White")
                undisplayed_image_count.grid(row=1, column=1, sticky="NSEW")
            else:
                # Only display one image
                image_file = products_bought[0].get("image_file")
                image = cWidget.Label(image_grid,
                                      image_file=image_file,
                                      image_width=76,
                                      image_height=76)
                image.grid(row=0, column=0, rowspan=2, columnspan=2, sticky="NSEW")

            product_one = products_bought[0].get("name")
            # Display product names
            if len(products_bought) == 1:
                products_string = f"{product_one} "
            else:
                # If more than one product, display count instead
                products_string = f"{product_one} + {len(products_bought) - 1} more..."
            order_cost = order.get("total_cost")
            data = [["Order ID", order_id],
                    ["Products", products_string],
                    ["Delivery status", order.get("delivery_status")],
                    ["Total", f"£{order_cost:.2f}"],
                    ["Date", order.get("date")]]
            for data_count, data in enumerate(data):
                # If field is to be displayed on second row
                if data_count + 1 > 3:
                    heading_row = 2
                    column = 5 - data_count
                else:
                    heading_row = 0
                    column = data_count + 1
                heading_label = cWidget.Label(order_pocket,
                                              text=data[0],
                                              fg_color="White",
                                              font=("Poppins-Regular", 24),
                                              anchor="s")
                heading_label.grid(row=heading_row, column=column, sticky="SW")
                if data[0] == "Products":
                    # Allow product name display to be multiline to prevent clustering
                    data_label = cWidget.Label(order_pocket,
                                               text=data[1],
                                               fg_color="White",
                                               max_line_length=len(product_one))
                else:
                    data_label = cWidget.Label(order_pocket,
                                               text=data[1],
                                               fg_color="White")
                data_label.grid(row=heading_row + 1, column=column, sticky="NW")

            view_button = cWidget.FilledButton(order_pocket,
                                               command=lambda o_id=order_id: self.app.load_frame("PastOrderFrame",
                                                                                                 order_id=o_id),
                                               text="View more",
                                               bg_color="White")
            view_button.grid(row=2, column=3, rowspan=2, sticky="W")

        return order_page


class PastOrderFrame(cWidget.ParentFrame):
    """
    The screen that displays one particular past order

    Parameters
    ----------
    app : any
        The main window of the application
    """
    def __init__(self, app):
        super().__init__(app)
        self.app = app
        self.entry_widgets = {}
        self.card_dict = {}
        self.grid_rowconfigure(0, weight=8, uniform="uniform")
        self.grid_rowconfigure(1, weight=1, uniform="uniform")
        self.grid_rowconfigure(2, weight=14, uniform="uniform")
        self.grid_rowconfigure(3, weight=12, uniform="uniform")
        self.grid_rowconfigure(4, weight=1, uniform="uniform")
        self.grid_rowconfigure(5, weight=3, uniform="uniform")
        self.grid_rowconfigure(6, weight=1, uniform="uniform")
        self.grid_columnconfigure(0, weight=9, uniform="uniform")
        self.grid_columnconfigure(1, weight=4, uniform="uniform")

        # Top-bar
        self.topbar = cWidget.Topbar(self, app, "Order ID: N/A")
        self.topbar.grid(row=0, column=0, columnspan=2, sticky="NSEW")

        # Initialise empty basket frame (view-only)
        self.basket_frame = cWidget.Basket(self, app, view_only=True)
        self.basket_frame.grid(row=2, column=0, rowspan=3, padx=10,  sticky="NSEW")

        # Initialise empty order information frame
        outer_frame = cWidget.Frame(self, border_width=1)
        outer_frame.grid(row=2, column=1, padx=10, rowspan=4, sticky="NSEW")
        outer_frame.grid_rowconfigure(0, weight=1)
        outer_frame.grid_columnconfigure(0, weight=1)
        self.order_info_frame = cWidget.ScrollableFrame(outer_frame)
        self.order_info_frame.grid_columnconfigure(0, weight=1, uniform="uniform")
        self.order_info_frame.grid(row=0, column=0, padx=2, pady=2, sticky="NSEW")

        self.title_frame = cWidget.Frame(self.order_info_frame, border_width=0)
        self.title_frame.grid(row=0, column=0, padx=10, pady=2, sticky="NSEW")
        self.title_frame.grid_columnconfigure(0, weight=3, uniform="uniform")
        self.title_frame.grid_columnconfigure(1, weight=1, uniform="uniform")
        self.title_frame.grid_columnconfigure(2, weight=1, uniform="uniform")
        title_label = cWidget.Label(self.title_frame, text="Your receipt", font=("Poppins Regular", 20))
        title_label.grid(row=0, column=0, sticky="NSW")

        self.button_frame = cWidget.Frame(self)
        self.button_frame.grid(row=5, column=0, sticky="NSEW")
        self.button_frame.grid_rowconfigure(0, weight=1)
        self.button_frame.grid_columnconfigure(0, weight=1, uniform="uniform")
        self.button_frame.grid_columnconfigure(1, weight=1, uniform="uniform")
        self.button_frame.grid_columnconfigure(2, weight=1, uniform="uniform")
        self.button_frame.grid_columnconfigure(3, weight=1, uniform="uniform")

    def refresh(self, order_id=None):
        """
        Updates the past order screen to its most recent state

        Parameters
        ----------
        order_id : int
            The ID of the order
        """
        self.entry_widgets = {}
        order = crud.search_table("ecommerce", "Orders", ["*"], f"order_id = '{order_id}'")[0]

        # Refresh basket
        products_bought = crud.search_joined_table("ecommerce",
                                                   "Order_Product",
                                                   [["Product", "product_id"]],
                                                   ["*"],
                                                   f"order_id = {order_id}")
        self.basket_frame.refresh(overwrite_with=products_bought)

        # Refresh order information
        self.topbar.change_title(f"Order ID: {order_id}")
        # Define attributes that cannot be edited
        unchangeable_rows = ["General",
                             f"Order date: {order.get('date')}",
                             f"Delivery status: {order.get('delivery_status')}",
                             "Costs",
                             f"Subtotal: £{backend.calculate_subtotal(products_bought):.2f}",
                             f"Delivery: £{order.get('delivery_cost'):.2f}",
                             f"Total: £{order.get('total_cost'):.2f}",
                             "Delivered to"]

        previous_row = 0
        for count, row in enumerate(unchangeable_rows):
            row_label = cWidget.Label(self.order_info_frame,
                                      font=("Inter Regular", 16),
                                      text=row,
                                      fg_color="White")
            # Heading formatting
            if row == "General" or row == "Costs" or row == "Delivered to":
                row_label.configure(font=("Poppins Regular", 20))
                row_label.configure(anchor="s")
                row_label.grid(row=count+1, column=0, padx=10, pady=(3, 0), sticky="SW")
            # Information formatting
            else:
                row_label.grid(row=count+1, column=0, padx=10, sticky="W")
            previous_row = count + 1

        # Get all cards and place them into a dictionary
        all_cards = crud.search_table("ecommerce",
                                      "Payment_Card",
                                      ["*"],
                                      f"customer_id = '{self.app.get_current_user().get_personal_id()}'")

        # Place widgets for fields that may or may not be amendable depending on the delivery status
        if order.get("delivery_status") == "Pending":
            delivery_address_widget = cWidget.Entry(self.order_info_frame,
                                                    table_name="Orders",
                                                    field_name="delivery_address",
                                                    toggleable=True,
                                                    current_text=order.get("delivery_address"),
                                                    height=40,
                                                    font=("Inter Regular", 16))
            self.entry_widgets["delivery_address"] = delivery_address_widget

            delivery_postcode_widget = cWidget.Entry(self.order_info_frame,
                                                     table_name="Orders",
                                                     field_name="delivery_postcode",
                                                     toggleable=True,
                                                     current_text=order.get("delivery_postcode"),
                                                     height=40)
            self.entry_widgets["delivery_postcode"] = delivery_postcode_widget

            self.card_dict = {card.get('card_number'): card.get("payment_card_id") for card in
                              all_cards}
            # Record the original card's id
            original_card_dict = {key: payment_card_id for key, payment_card_id in self.card_dict.items()
                                  if payment_card_id == order.get("payment_card_id")}
            original_card_key, original_card_id = list(original_card_dict.items())[0]

            payment_method_widget = cWidget.Frame(self.order_info_frame, border_width=1)
            payment_method_widget.grid_rowconfigure(0, weight=1)
            payment_method_widget.grid_columnconfigure(0, weight=1)
            # The options of the dropdown become all the cards and the default is the original card used in the order
            card_dropdown = cWidget.Dropdown(payment_method_widget,
                                             values=list(self.card_dict.keys()),
                                             var_default=original_card_key)
            card_dropdown.grid(row=0, column=0, padx=2, pady=2, sticky="NSEW")
            self.entry_widgets["payment_card_id"] = card_dropdown
        else:
            delivery_address_widget = cWidget.Label(self.order_info_frame,
                                                    text=order.get("delivery_address"),
                                                    font=("Inter Regular", 16),
                                                    anchor="w")

            delivery_postcode_widget = cWidget.Label(self.order_info_frame,
                                                     text=order.get("delivery_postcode"),
                                                     font=("Inter Regular", 16),
                                                     anchor="w")
            # Error value in case finding the actual card number fails
            card_number = "N/A"
            for card in all_cards:
                if card.get("payment_card_id") == order.get("payment_card_id"):
                    card_number = card.get("card_number")
                    break
            payment_method_widget = cWidget.HideableLabel(self.order_info_frame,
                                                          text=f"{card_number}",
                                                          font=("Inter Regular", 12))

        delivery_address_widget.grid(row=previous_row+1, column=0, padx=10, sticky="NSEW")
        delivery_postcode_widget.grid(row=previous_row+2, column=0, padx=10, sticky="NSEW")
        billing_heading = cWidget.Label(self.order_info_frame,
                                        text="Billed to",
                                        font=("Poppins Regular", 20))
        billing_heading.grid(row=previous_row+3, column=0, padx=10, sticky="W")
        payment_method_widget.grid(row=previous_row+4, column=0, padx=10, sticky="EW")

        download_receipt_button = cWidget.BlankButton(self.title_frame,
                                                      image_file="download_icon.png",
                                                      image_width=15,
                                                      image_height=15,
                                                      command=lambda: self.create_report(order_id, "download"))
        download_receipt_button.grid(row=0, column=1, sticky="NSE")

        email_receipt_button = cWidget.BlankButton(self.title_frame,
                                                   image_file="email_icon.png",
                                                   image_width=15,
                                                   image_height=15,
                                                   command=lambda: self.create_report(order_id, "email"))
        email_receipt_button.grid(row=0, column=2, sticky="NSE")

        reorder_button = cWidget.FilledButton(self.button_frame,
                                              command=lambda: self.reorder(products_bought),
                                              text="Reorder",
                                              height=10,
                                              bg_color="White")
        reorder_button.grid(row=0, column=0, padx=10, sticky="SEW")

        # If the order can be changed, allow changes to be saved and cleared and allow the order to be deleted
        if order.get("delivery_status") == "Pending":
            save_changes_button = cWidget.FilledButton(self.button_frame,
                                                       command=lambda: self.update_order(order),
                                                       text="Save changes",
                                                       height=10,
                                                       bg_color="White")
            save_changes_button.grid(row=0, column=1, padx=10, sticky="SEW")

            clear_changes_button = cWidget.FilledButton(self.button_frame,
                                                        command=lambda: self.refresh(order_id),
                                                        text="Clear changes",
                                                        height=10,
                                                        bg_color="White")
            clear_changes_button.grid(row=0, column=2, padx=10, sticky="SEW")

            delete_button = cWidget.FilledButton(self.button_frame,
                                                 command=lambda: self.delete_order(order),
                                                 text="Delete",
                                                 height=10,
                                                 bg_color="White")
            delete_button.grid(row=0, column=3, padx=10, sticky="SEW")

    def update_order(self, order: dict):
        """
        Update the details of the order

        Parameters
        ----------
        order : dict
            The order data structure
        """
        proposed_update_data = {}
        input_validities = []
        for field_name, entry_widget in self.entry_widgets.items():
            if field_name == "payment_card_id":
                # If the dropdown value has changed
                if entry_widget.get() != entry_widget.get_default():
                    proposed_update_data["payment_card_id"] = self.card_dict.get(entry_widget.get())
            else:
                # If field has changed and is not blank
                if entry_widget.get() != order.get(field_name) and entry_widget.get() != "":
                    proposed_update_data[field_name] = entry_widget.get()
                    input_validities.append(entry_widget.check_if_valid())

        # If a field has changed
        if proposed_update_data:
            print(input_validities)
            if False not in input_validities:
                crud.update_record("ecommerce",
                                   "Orders",
                                   proposed_update_data,
                                   f"order_id = '{order.get('order_id')}'")
                self.refresh(order.get("order_id"))
                mbox.showinfo("Success!", "Order successfully updated!")
            else:
                mbox.showerror("Error!", "Input invalid!")

    def delete_order(self, order: dict):
        """
        Delete a pending order

        Parameters
        ----------
        order : dict
            The order data structure
        """
        # Warns the user of the consequences
        delete_confirmed = mbox.askyesnocancel("Warning!", """This action is PERMANENT and will DELETE THIS ORDER.
        \nAre you sure you want to continue?""")
        if delete_confirmed:
            delete_id = order.get("order_id")
            products_bought = crud.search_table("ecommerce",
                                                "Order_Product",
                                                ["*"],
                                                f"order_id = '{delete_id}'")
            crud.delete_record("ecommerce",
                               "Orders",
                               f"order_id = '{delete_id}'")
            # Update stock and total sold
            for product in products_bought:
                backend.update_total_sold(product.get("product_id"))
                backend.decrease_stock_by(product.get("product_id"), -int(product.get("quantity")))
            self.app.load_frame("MyOrdersFrame")
            mbox.showinfo("Success!", "Order successfully deleted!")

    def reorder(self, products_bought=None):
        """
        Place the same order into the basket

        Parameters
        ----------
        products_bought : list
            The products bought in the order
        """
        if products_bought:
            message = "The following products are unavailable and cannot be reordered:"
            popup_needed = False
            products_available = []
            for product in products_bought:
                # Do not add any products which are unavailable
                if product.get("current_stock") == 0:
                    message += f"\n - {product.get('name')}"
                    popup_needed = True
                else:
                    products_available.append(product)

            if products_available:
                basket = self.app.get_current_user().get_basket()
                basket.reset_basket()
                for product in products_available:
                    basket.add(product)

                if popup_needed:
                    mbox.showinfo("Info", message)
                self.app.load_frame("BasketFrame")
            else:
                mbox.showinfo("Info", message)

    def create_report(self, order_id: int, mode: str):
        """
        Create an order receipt

        Parameters
        ----------
        order_id : int
            The ID of the order

        mode : str
            The mode which determines how the report is stored, either 'email' or 'download'
        """
        summary_report_manager = self.app.expand_summary_report_manager()
        summary_report_manager.create_report(report_name="Order receipt",
                                             mode=mode,
                                             order_id=order_id)


class ProcessingOrderFrame(cWidget.ParentFrame):
    """
    The screen that displays a loading animation whilst an order is processing

    Parameters
    ----------
    app : any
        The main window of the application
    """
    def __init__(self, parent: any):
        super().__init__(parent, fg_color=colours.get_primary_colour())
        self.app = parent
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        content_frame = tk.Frame(self,
                                 bg=colours.get_primary_colour())
        content_frame.grid(row=0,
                           column=0,
                           sticky="EW")

        heading_label = cWidget.Label(content_frame,
                                      text="Please do not close the application.",
                                      max_line_length=25,
                                      justify="center",
                                      font=("Poppins Regular", 48),
                                      fg_color=colours.get_primary_colour())
        heading_label.pack()

        self.progress_bar = cWidget.ImageProgressBar(content_frame,
                                                     image_width=200,
                                                     image_height=250,
                                                     span=900,
                                                     fg_color=colours.get_primary_colour(),
                                                     border_width=0,
                                                     mode="indeterminate",
                                                     indeterminate_style="bounce",
                                                     start_off=True,
                                                     end_off=True)
        self.progress_bar.pack()

        info_label = cWidget.Label(content_frame,
                                   text="We are currently processing your order.",
                                   font=("Inter Regular", 32),
                                   fg_color=colours.get_primary_colour())
        info_label.pack()

    def refresh(self, card_info: dict = None, new_card_created: bool = None, delivery_info: dict = None):
        """
        Restart the loading animation and process a new order

        Parameters
        ----------
        card_info : dict
            The payment card data for the order

        new_card_created : bool
            Whether a new card should be created

        delivery_info : dict
            The delivery data for the order
        """
        def process_order():
            """
            Completes processing for an order
            """
            # Process order
            order_id, was_email_sent = backend.process_order(self.app.get_current_user(), card_info, new_card_created, delivery_info)
            # Stop progress bar and display confirmation
            self.progress_bar.reset()
            self.app.load_frame("ConfirmationFrame", order_id=order_id, email_was_successful=was_email_sent)

        self.progress_bar.start(interval=10)

        # Initialise a thread to process the order whilst the loading animation continues running
        order_thread = threading.Thread(target=process_order)
        # Daemon attribute will kill the thread once the main execution ends
        order_thread.daemon = True
        order_thread.start()


class DatabaseManagementFrame(cWidget.ParentFrame):
    """
    The screen that controls database management for staff stakeholders

    Parameters
    ----------
    app : any
        The main window of the application
    """
    def __init__(self, app: any):
        super().__init__(app)
        self.grid_rowconfigure(0, weight=1, uniform="uniform")
        self.grid_rowconfigure(1, weight=4, uniform="uniform")
        self.grid_rowconfigure(2, weight=4, uniform="uniform")
        self.grid_columnconfigure(0, weight=8, uniform="uniform")
        self.grid_columnconfigure(1, weight=4, uniform="uniform")
        self.app = app

        self.treeview = None
        self.table_name = None

        title_frame = cWidget.Frame(self)
        title_frame.grid(row=0, column=0, sticky="W")

        hamburger_button = cWidget.BlankButton(title_frame,
                                               width=30,
                                               image_file="hamburger_icon.png",
                                               image_width=30,
                                               image_height=30,
                                               command=lambda: self.app.expand_staff_sidebar())
        hamburger_button.grid(row=0, column=0)
        self.title_label = cWidget.Label(title_frame,
                                         text="",
                                         font=("Poppins Regular", 36))
        self.title_label.grid(row=0, column=1, padx=20)
    
        action_frame = cWidget.Frame(self, border_width=1)
        action_frame.grid(row=1, column=1, padx=(0, 20), sticky="NSEW")
        action_frame.grid_rowconfigure(0, weight=1, uniform="uniform")
        action_frame.grid_rowconfigure(1, weight=1, uniform="uniform")
        action_frame.grid_columnconfigure(0, weight=1)

        mode_frame = cWidget.Frame(action_frame)
        mode_frame.grid(row=0, column=0, padx=5, pady=5, sticky="NSEW")
        mode_frame.grid_columnconfigure(0, weight=1)

        mode_subheading = cWidget.Label(mode_frame,
                                        text="Mode",
                                        font=("Poppins Regular", 24))
        mode_subheading.grid(row=0, column=0, sticky="W")

        self.radio_var = tk.StringVar(mode_frame, "Search")
        self.current_mode = "Search"
        modes = ["Create", "Search", "Update"]
        # Create radio buttons for different modes
        for count, mode in enumerate(modes):
            radio_button = ctk.CTkRadioButton(mode_frame,
                                              variable=self.radio_var,
                                              value=mode,
                                              command=lambda: self.change_mode(),
                                              text=mode,
                                              font=("Inter Regular", 16))
            radio_button.grid(row=count+1, column=0, sticky="W")

        # Create frame for reports
        self.reports_frame = cWidget.Frame(action_frame)
        self.reports_frame.grid(row=1, column=0, padx=5, pady=5, sticky="NSEW")
        self.reports_frame.grid_propagate(False)
        self.reports_frame.grid_columnconfigure(0, weight=3, uniform="uniform")
        self.reports_frame.grid_columnconfigure(1, weight=1, uniform="uniform")
        self.reports_frame.grid_columnconfigure(2, weight=1, uniform="uniform")
        self.reports_frame.grid_rowconfigure(0, weight=2, uniform="uniform")
        for n in range(4):
            self.reports_frame.grid_rowconfigure(n+1, weight=1, uniform="uniform")

        input_frame = cWidget.Frame(self, border_width=1)
        input_frame.grid(row=1, column=0, padx=(20, 10), sticky="NSEW")
        input_frame.grid_rowconfigure(0, weight=1, uniform="uniform")
        input_frame.grid_rowconfigure(1, weight=3, uniform="uniform")
        input_frame.grid_rowconfigure(2, weight=1, uniform="uniform")
        input_frame.grid_columnconfigure(0, weight=1)

        self.input_title = cWidget.Label(input_frame,
                                         text="Actions",
                                         font=("Poppins Regular", 24))
        self.input_title.grid(row=0, column=0, padx=5, pady=(5, 0), sticky="W")

        # Entity entry frame
        self.entry_frame = cWidget.ScrollableFrame(input_frame)
        self.entry_frame.grid_columnconfigure(0, weight=1, uniform="uniform")
        self.entry_frame.grid_columnconfigure(1, weight=1, uniform="uniform")
        self.entry_frame.grid_columnconfigure(2, weight=1, uniform="uniform")
        self.entry_frame.grid(row=1, column=0, padx=5, pady=5, sticky="NSEW")
        self.entry_widgets = {}

        # Button frame
        self.button_frame = cWidget.Frame(input_frame)
        self.button_frame.grid(row=2, column=0, padx=5, pady=5, sticky="NSEW")
        self.button_frame.grid_columnconfigure(0, weight=2, uniform="uniform")
        self.button_frame.grid_columnconfigure(1, weight=2, uniform="uniform")
        self.button_frame.grid_columnconfigure(2, weight=3, uniform="uniform")
        self.button_frame.grid_columnconfigure(3, weight=3, uniform="uniform")
        clear_button = cWidget.FilledButton(self.button_frame,
                                            height=28,
                                            command=lambda: self.reset_entry_frame(),
                                            text="Clear input",
                                            font=("Inter Regular", 16),
                                            bg_color=colours.get_bg_colour())
        clear_button.grid(row=0, column=0, padx=2, sticky="NEW")
        self.action_button = cWidget.FilledButton(self.button_frame,
                                                  height=28,
                                                  command=lambda: self.perform_action(),
                                                  text=self.current_mode,
                                                  font=("Inter Regular", 16),
                                                  bg_color=colours.get_bg_colour())
        self.action_button.grid(row=0, column=1, padx=2, sticky="NEW")
        reset_treeview_button = cWidget.FilledButton(self.button_frame,
                                                     height=28,
                                                     command=lambda: self.reset_treeview(),
                                                     text="Reset treeview",
                                                     font=("Inter Regular", 16),
                                                     bg_color=colours.get_bg_colour())
        reset_treeview_button.grid(row=0, column=2, padx=2, sticky="NEW")
        self.delete_selected_button = cWidget.FilledButton(self.button_frame,
                                                           height=28,
                                                           command=lambda: self.delete_selected(),
                                                           text="Delete selected",
                                                           font=("Inter Regular", 16),
                                                           bg_color=colours.get_bg_colour())

        self.timeframe_splash = None

    def change_mode(self):
        """
        Change the database's mode to either 'search', 'update' or 'create'
        """
        # If the user has sufficient access
        if backend.check_access(access_level=self.app.get_current_user().get_access_level(),
                                table_name=self.table_name,
                                mode=self.radio_var.get()[0]):
            self.current_mode = self.radio_var.get()
            self.action_button.configure(text=self.current_mode)
            self.reset_entry_frame()
        else:
            mbox.showerror("Error!", f"You do not have access to {self.radio_var.get().lower()} this entity!")
            self.radio_var.set(self.current_mode)

    def reset_entry_frame(self):
        """
        Update the fields that can be edited / input
        """
        for widget in self.entry_frame.winfo_children():
            widget.destroy()
        self.entry_widgets = {}

        # Enables deletion for management staff only
        if self.app.get_current_user().get_access_level() != "Sales":
            self.delete_selected_button.grid(row=0, column=3, padx=2, sticky="NEW")
        else:
            self.delete_selected_button.grid_forget()

        all_field_headings = crud.get_table_headings("ecommerce",
                                                     table_name=self.table_name)

        if self.current_mode == "Create" or self.current_mode == "Update":
            validate_input = True
            # Take away fields that are automatic i.e. cannot be altered by the user
            non_pk_fields = all_field_headings[1:]
            needed_fields = [f"{field}" for field in non_pk_fields]
            if self.table_name == "Product":
                needed_fields.remove("average_rating")
                needed_fields.remove("total_sold")
                needed_fields.remove("image_file")
            if self.table_name == "Orders":
                needed_fields.remove("date")
                needed_fields.remove("delivery_address")
                needed_fields.remove("delivery_postcode")
                needed_fields.remove("delivery_cost")
                needed_fields.remove("total_cost")
                needed_fields.remove("customer_id")
                needed_fields.remove("payment_card_id")
        else:
            needed_fields = all_field_headings
            # Special case
            if self.table_name == "Product":
                needed_fields.remove("image_file")
            validate_input = False

        # Format all fields
        display_fields = {needed_field: backend.convert_field_name_style(needed_field) for needed_field in needed_fields}

        # Display fields in a 3x? grid
        for count, (field_name, display_field) in enumerate(display_fields.items()):
            heading_row = 2 * (count // 3)
            column = count % 3
            field_heading = cWidget.Label(self.entry_frame,
                                          text=display_field)
            field_heading.grid(row=heading_row, column=column, padx=(0, 5), sticky="W")
            entry_widget = cWidget.Entry(self.entry_frame,
                                         validated=validate_input,
                                         table_name=self.table_name,
                                         field_name=field_name)
            entry_widget.grid(row=heading_row+1, column=column, padx=(0, 5), sticky="EW")
            self.entry_widgets[needed_fields[count]] = entry_widget
            final_row = heading_row + 1
            final_column = column

        # If any fields use list validation
        if self.table_name == "Product" or self.table_name == "Staff" or self.table_name == "Orders":
            # Set up dropdown menu to display
            if self.table_name == "Product":
                all_records = crud.search_table("ecommerce",
                                                "Supplier",
                                                ["*"],
                                                "")
                current_suppliers = ["Not applied"] + sorted({str(record.get("supplier_id")) for record in all_records})
                dropdown_fields = {"category": ["Not applied", "Rackets", "Balls", "Clothing", "Equipment"],
                                   "supplier_id": current_suppliers}
            elif self.table_name == "Staff":
                dropdown_fields = {"access_level": ["Not applied", "Management", "Sales"]}
            elif self.table_name == "Orders":
                dropdown_fields = {"delivery_status": ["Not applied", "Pending", "Delivered"]}

            for field_name, possible_values in dropdown_fields.items():
                dropdown_frame = cWidget.Frame(self.entry_frame,
                                               border_width=1)
                # Overwrite field entry widget with dropdown instead
                if field_name == "category":
                    if self.current_mode != "Search":
                        row = 1
                        column = 2
                    else:
                        row = 3
                        column = 0
                elif field_name == "delivery_status":
                    if self.current_mode != "Search":
                        row = 1
                        column = 0
                    else:
                        row = 5
                        column = 0
                else:
                    row = final_row
                    column = final_column
                dropdown_frame.grid(row=row, column=column, padx=(0, 5), sticky="EW")
                dropdown_frame.grid_columnconfigure(0, weight=1)
                dropdown_var = possible_values[0]
                dropdown = cWidget.Dropdown(dropdown_frame,
                                            var_default=dropdown_var,
                                            values=possible_values)
                dropdown.grid(row=0, column=0, padx=2, pady=2, sticky="NSEW")
                self.entry_widgets[field_name] = dropdown

    def reset_reports(self):
        """
        Update the reports available for that entity
        """
        for widget in self.reports_frame.winfo_children():
            widget.destroy()
        reports_heading = cWidget.Label(self.reports_frame,
                                        text="Reports",
                                        font=("Poppins Regular", 24))
        reports_heading.grid(row=0, column=0, columnspan=3, sticky="W")
        # Get any reports available
        if self.table_name == "Orders":
            reports = ["Order receipt"]
        elif self.table_name == "Product":
            reports = ["Best selling products",
                       "Product performance"]
        else:
            reports = None

        if reports is None:
            pass
        else:
            for count, report in enumerate(reports):
                report_name_label = cWidget.Label(self.reports_frame,
                                                  text=report,
                                                  font=("Poppins Regular", 14))
                report_name_label.grid(row=count+1, column=0, sticky="W")
                download_button = cWidget.BlankButton(self.reports_frame,
                                                      command=lambda r=report: self.create_report(r, "download"),
                                                      image_file="download_icon.png",
                                                      image_width=20,
                                                      image_height=20)
                download_button.grid(row=count+1, column=1, sticky="E")
                email_button = cWidget.BlankButton(self.reports_frame,
                                                   command=lambda r=report: self.create_report(r, "email"),
                                                   image_file="email_icon.png",
                                                   image_width=20,
                                                   image_height=20)
                email_button.grid(row=count+1, column=2, sticky="E")

    def reset_treeview(self):
        """
        Reset the treeview to show all records for an entity
        """
        # Populate the treeview with all entity records
        self.treeview.populate_tree(crud.search_table("ecommerce",
                                    self.table_name,
                                    ["*"],
                                    ""))

    def delete_selected(self):
        """
        Delete a record selected in the treeview
        """
        selected_values = self.treeview.get_selected_values()
        # If a record is selected
        if not selected_values:
            mbox.showerror("Error!", "No record selected!")
        else:
            # Set admin account to not be modified
            if self.table_name == "Staff" and self.treeview.get_selected_values()[0] == 1:
                mbox.showerror("Error!", "You cannot delete the admin account.")
            elif self.table_name == "Orders" and self.treeview.get_selected_values()[6] == "Delivered":
                mbox.showerror("Error!", "You cannot delete an order that has already been delivered!")
            else:
                # Get the id field name and the corresponding id value so that the record can be deleted
                id_value = selected_values[0]
                id_field_name = crud.get_table_headings("ecommerce",
                                                        self.table_name)[0]

                # If a customer is being deleted
                if id_field_name == "customer_id":
                    # For all pending orders deleted, refund the stock
                    orders_pending = crud.search_table("ecommerce",
                                                       "Orders",
                                                       ["*"],
                                                       f"customer_id = '{id_value}' AND delivery_status = 'Pending'")
                    products_per_order = []
                    for order in orders_pending:
                        products_bought = crud.search_table("ecommerce",
                                                            "Order_Product",
                                                            ["*"],
                                                            f"order_id = '{order.get('order_id')}'")
                        products_per_order.append(products_bought)
                        for product in products_bought:
                            backend.decrease_stock_by(product.get("product_id"), -(product.get("quantity")))

                    ratings_to_delete = crud.search_table("ecommerce", "Ratings", "*", f"customer_id = '{id_value}'")

                    crud.delete_record("ecommerce",
                                       self.table_name,
                                       f"{id_field_name} = '{id_value}'")

                    # Update product ratings for every product the user rated
                    for rating in ratings_to_delete:
                        backend.update_product_rating(rating.get("product_id"))

                    # For all pending orders deleted, decrease the total sold
                    for products_bought in products_per_order:
                        for product in products_bought:
                            backend.update_total_sold(product.get("product_id"))

                # If an order or payment card is being deleted
                elif id_field_name == "order_id" or id_field_name == "payment_card_id":
                    if id_field_name == "order_id":
                        # For all pending orders deleted, refund the stock
                        orders_pending = crud.search_table("ecommerce",
                                                           "Orders",
                                                           ["*"],
                                                           f"order_id = '{id_value}' AND delivery_status = 'Pending'")
                    else:
                        orders_pending = crud.search_table("ecommerce",
                                                           "Orders",
                                                           ["*"],
                                                           f"payment_card_id = '{id_value}' AND delivery_status = 'Pending'")
                    products_per_order = []
                    for order in orders_pending:
                        products_bought = crud.search_table("ecommerce",
                                                            "Order_Product",
                                                            ["*"],
                                                            f"order_id = '{order.get('order_id')}'")
                        products_per_order.append(products_bought)
                        for product in products_bought:
                            backend.decrease_stock_by(product.get("product_id"), -(product.get("quantity")))

                    crud.delete_record("ecommerce",
                                       self.table_name,
                                       f"{id_field_name} = '{id_value}'")

                    # For all pending orders deleted, decrease the total sold
                    for products_bought in products_per_order:
                        for product in products_bought:
                            backend.update_total_sold(product.get("product_id"))

                # If a rating is being deleted
                elif id_field_name == "rating_id":
                    # Update the product that was rated
                    rating_to_delete = crud.search_table("ecommerce", "Ratings", "*", f"rating_id = '{id_value}'")[0]

                    crud.delete_record("ecommerce",
                                       self.table_name,
                                       f"{id_field_name} = '{id_value}'")

                    if rating_to_delete:
                        backend.update_product_rating(rating_to_delete.get("product_id"))
                else:
                    crud.delete_record("ecommerce",
                                       self.table_name,
                                       f"{id_field_name} = '{id_value}'")
                self.treeview.delete_selected_record()

    def perform_action(self):
        """
        Attempt to either 'create', 'search' for or 'update' a record depending on the current mode
        """
        user_entry = {field_name: entry_widget.get() for field_name, entry_widget in self.entry_widgets.items()}
        # Check that input has been given for create and search mode
        if (
                list(user_entry.values()).count("") + list(user_entry.values()).count("Not applied") == len(user_entry)
                and self.current_mode != "Update"
        ):
            mbox.showerror("Error!", "No input given")
        else:
            if self.current_mode == "Search":
                # Search where field_name = value on fields that the user entered input for
                search_parameters = [f"{field_name} = '{backend.encrypt(field_name, value)}'"
                                     for count, (field_name, value) in enumerate(user_entry.items())
                                     if value not in ["", "Not applied"]]
                matched_records = crud.search_table("ecommerce",
                                                    self.table_name,
                                                    ["*"],
                                                    "AND ".join(search_parameters))
                self.treeview.populate_tree(matched_records)
            else:
                if self.current_mode == "Create":
                    input_validity = [entry_widget.check_if_valid() for entry_widget in self.entry_widgets.values()
                                      if str(type(entry_widget)) == "<class 'custom_widgets.Entry'>"]
                    if False in input_validity:
                        mbox.showerror("Error!", "Invalid input!")
                    else:
                        should_continue = True
                        if self.table_name == "Product":
                            # Add in automatic fields
                            user_entry["total_sold"] = 0
                            user_entry["average_rating"] = 0
                            # Get product image
                            image_file = self.app.expand_image_manager()
                            # If the user did not pick an image
                            if not image_file:
                                should_continue = False
                            else:
                                user_entry["image_file"] = image_file

                        if should_continue:
                            crud.add_record("ecommerce",
                                            self.table_name,
                                            user_entry)
                            self.reset_treeview()
                            self.reset_entry_frame()
                            mbox.showinfo("Success!", f"{self.table_name} record created successfully!")
                else:
                    # If no treeview record is selected
                    if not self.treeview.get_selected_values():
                        mbox.showerror("Error!", "No record selected to update!")
                    else:
                        input_validity = [entry_widget.check_if_valid() for entry_widget in self.entry_widgets.values()
                                          if str(type(entry_widget)) == "<class 'custom_widgets.Entry'>"
                                          and entry_widget.get() not in ["", "Not Applied"]]
                        if False in input_validity:
                            mbox.showerror("Error!", "Input invalid!")
                        else:
                            if self.table_name == "Product":
                                # Check if the user wants to change the image
                                new_image_file = self.app.expand_image_manager(existing_image_file=self.treeview.get_selected_values()[9])
                                if new_image_file != self.treeview.get_selected_values()[9]:
                                    user_entry["image_file"] = new_image_file

                            if self.table_name == "Staff" and self.treeview.get_selected_values()[0] == 1:
                                mbox.showerror("Error!", "You cannot update the admin account.")
                            else:
                                # Get the field name for the table's primary key
                                record_id_name = crud.get_table_headings("ecommerce", self.table_name)[0]
                                # Get the field value for the record's primary key
                                record_id = self.treeview.get_selected_values()[0]
                                # Update field_name with value on fields that the user entered input for
                                field_values = {f"{field_name}": f"{value}"
                                                for field_name, value in user_entry.items()
                                                if value not in ["", "Not applied"]}
                                if field_values:
                                    crud.update_record("ecommerce",
                                                       self.table_name,
                                                       field_values,
                                                       f"{record_id_name} = '{record_id}'")
                                    self.reset_treeview()
                                    self.reset_entry_frame()
                                    mbox.showinfo("Success!", f"{self.table_name} record updated successfully!")

    def create_report(self,
                      report_name: Literal["Order receipt", "Best selling products", "Product performance"],
                      mode: Literal["download", "email"],):
        """
        Loads in the summary report manager to create a report

        Parameters
        ----------
        report_name : str
            The name of the report

        mode : str
            The mode that determines how the report is stored, either 'download' or 'email'
        """
        if report_name == "Order receipt":
            # If no order is selected
            if not self.treeview.get_selected_values():
                mbox.showerror("Error!", "No order record selected!")
            else:
                order_id = self.treeview.get_selected_values()[0]
                customer_id = self.treeview.get_selected_values()[-2]
                customer = crud.search_record("ecommerce",
                                              "Customer",
                                              ["*"],
                                              f"customer_id = {customer_id}")
                full_name = f"{customer.get('name')} {customer.get('surname')}"
                # Open summary report manager
                summary_report_manager = self.app.expand_summary_report_manager()
                summary_report_manager.create_report(report_name=report_name,
                                                     mode=mode,
                                                     order_id=order_id,
                                                     full_name=full_name)
        elif report_name == "Best selling products":
            # Open summary report manager
            summary_report_manager = self.app.expand_summary_report_manager()
            summary_report_manager.create_report(report_name=report_name, mode=mode)
        else:
            # If no product is selected
            if not self.treeview.get_selected_values():
                mbox.showerror("Error!", "No product selected!")
            else:
                # Open summary report manager
                summary_report_manager = self.app.expand_summary_report_manager()
                summary_report_manager.create_report(report_name=report_name,
                                                     mode=mode,
                                                     product_id=self.treeview.get_selected_values()[0])

    def refresh(self,
                table_name: str):
        """
        Update the database screen to its most recent state

        Parameters
        ----------
        table_name : str
            The name of the table which should be activated
        """
        self.app.staff_sidebar.change_table(table_name, trigger_command=False)
        self.change_table(table_name)
        self.radio_var.set("Search")
        self.change_mode()

    def change_table(self,
                     table_name: str):
        """
        Change the table that is currently active

        Parameters
        ----------
        table_name : str
            The name of the table which should be activated
        """
        self.table_name = table_name
        entity_name = self.app.staff_sidebar.get_entity_name()
        self.title_label.configure(text=entity_name)
        self.reset_entry_frame()
        self.reset_reports()

        if self.treeview:
            self.treeview.destroy()
        # Create treeview for the table
        columns = [backend.convert_field_name_style(field)[:-1] for field in crud.get_table_headings("ecommerce", table_name=self.table_name)]
        self.treeview = cWidget.Treeview(self, columns)
        self.treeview.grid(row=2, column=0, columnspan=2, padx=30, pady=10, sticky="NSEW")
        all_records = crud.search_table("ecommerce",
                                        self.table_name,
                                        ["*"],
                                        "")
        self.treeview.populate_tree(all_records)


class SummaryReportController(ctk.CTkToplevel):
    """
    Toplevel that controls summary report creation

    Parameters
    ----------
    parent : any
        pass

    app : any
        pass
    """
    def __init__(self, parent: any, app: any):
        super().__init__(parent, fg_color=colours.get_primary_colour())
        # Attributes
        self.app = app
        self.report_name = None
        self.mode = None

        # Metadata
        self.geometry("600x600")
        self.title("Turtle Tennis - Report Manager")
        self.transient(parent)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Widgets
        self.info_frame = cWidget.Frame(self, fg_color=colours.get_primary_colour())
        self.info_frame.grid(row=0, column=0)

        self.progress_bar = cWidget.ImageProgressBar(self.info_frame,
                                                     image_width=100,
                                                     image_height=100,
                                                     span=400,
                                                     fg_color=colours.get_primary_colour(),
                                                     border_width=0,
                                                     mode="indeterminate",
                                                     indeterminate_style="bounce",
                                                     start_off=True,
                                                     end_off=True)

    def create_report(self,
                      report_name: Literal["Product comparison", "Order receipt", "Best selling products", "Product performance"],
                      mode: Literal["download", "email"],
                      days_back: int = None,
                      **kwargs):
        """
        Create a particular summary report

        Parameters
        ----------
        report_name : str
            The name of the report

        mode : str
            The mode which determines how the report is stored, either 'download' or 'email'

        days_back : int
            The timeframe used for the 'Product performance' and 'Best selling products' reports
        """
        for widget in self.info_frame.winfo_children():
            widget.destroy()

        # If the report needs a timeframe yet none has been provided
        if (
                (report_name == "Product performance"
                 or report_name == "Best selling products")
                and days_back is None
        ):
            heading_label = cWidget.Label(self.info_frame,
                                          text="Please select a timeframe",
                                          max_line_length=14,
                                          justify="center",
                                          fg_color=colours.get_primary_colour(),
                                          font=("Poppins Regular", 48))
            heading_label.pack()

            timeframes = {"Today": 0,
                          "Last 7 days": 6,
                          "Last 14 days": 13,
                          "Last 30 days": 29}
            # Display timeframe options
            for timeframe, new_days_back in timeframes.items():
                # The button which use recursion to run this function again, this time with a timeframe
                timeframe_button = cWidget.FilledButton(self.info_frame,
                                                        text=timeframe,
                                                        command=lambda d_b=new_days_back: self.create_report(report_name=report_name,
                                                                                                             mode=mode,
                                                                                                             days_back=d_b,
                                                                                                             **kwargs))
                timeframe_button.pack(pady=5)
        else:
            self.report_name = report_name
            self.mode = mode

            # Display a loading bar and message whilst the report is being processed
            heading_label = cWidget.Label(self.info_frame,
                                          text="Please do not close this window.",
                                          max_line_length=20,
                                          justify="center",
                                          font=("Poppins Regular", 48),
                                          fg_color=colours.get_primary_colour())
            heading_label.pack()
            self.progress_bar = cWidget.ImageProgressBar(self.info_frame,
                                                         image_width=100,
                                                         image_height=100,
                                                         span=400,
                                                         fg_color=colours.get_primary_colour(),
                                                         border_width=0,
                                                         mode="indeterminate",
                                                         indeterminate_style="bounce")
            self.progress_bar.pack()
            self.progress_bar.start()

            subheading_label = cWidget.Label(self.info_frame,
                                             text="We are creating your summary report.",
                                             max_line_length=21,
                                             justify="center",
                                             font=("Inter Regular", 32),
                                             fg_color=colours.get_primary_colour())
            subheading_label.pack()

            def process_report():
                """
                Processes the report to be generated
                """
                current_user = self.app.get_current_user()
                email_address = current_user.get_email()
                name = current_user.get_name()
                # For each report, create it and set any email content if needed
                if self.report_name == "Product performance":
                    product_id = kwargs.get("product_id")
                    report_pdf = backend.create_product_summary(product_id=product_id, days_back=days_back)
                    email_subject = "Your requested product performance report"
                    email_body = f"Hi {name}, here is that product performance report you wanted!"
                elif self.report_name == "Best selling products":
                    report_pdf = backend.create_best_selling_report(days_back=days_back)
                    email_subject = "Your requested best selling products report"
                    email_body = f"Hi {name}, here is that best selling product report you wanted!"
                elif self.report_name == "Order receipt":
                    order_id = kwargs.get("order_id")
                    full_name = f"{name} {current_user.get_surname()}"
                    report_pdf = backend.create_receipt(order_id, full_name=full_name)
                    email_subject = "Your order receipt"
                    email_body = f"""Hi {name}, thanks for ordering with us!\nHere is a copy of your receipt. 
                                You can also view your past orders on the 'order history' section of our app!"""
                else:
                    product_one = kwargs.get("product_one")
                    product_two = kwargs.get("product_two")
                    report_pdf = backend.create_comparison_report(product_one, product_two)
                    email_subject = "Your product comparison"
                    email_body = f"Hi {name}, here's that amazing product comparison you made!"

                if self.mode != "email":
                    self.progress_bar.stop()
                    self.destroy()
                    mbox.showinfo("Success!", f"Download successful!\nFile name: {report_pdf}")
                else:
                    email_successful = backend.send_email(to_address=email_address,
                                                          subject=email_subject,
                                                          body_text=email_body,
                                                          attachments=[report_pdf])
                    self.progress_bar.stop()
                    self.destroy()
                    if email_successful:
                        mbox.showinfo("Success!", f"The report has been sent to your email!")
                    else:
                        mbox.showerror("Error!", f"The email could not be sent. The file has been downloaded to: {report_pdf}")
                return

            # Disable matplotlib warning
            warnings.filterwarnings("ignore")
            # Run processing in a thread to allow the progressbar to maintain active whilst processing
            report_thread = threading.Thread(target=process_report)
            report_thread.daemon = True
            report_thread.start()


class ImageController(ctk.CTkToplevel):
    """
    Toplevel that prompts for an image

    Parameters
    ----------
    parent : any
        pass

    app : any
        pass

    existing_image_file : str
        An image that exists already for the purpose specified
    """
    def __init__(self, parent: any, app: any, existing_image_file: str = ""):
        super().__init__(parent, fg_color=colours.get_primary_colour())
        # Attributes
        self.app = app

        # Metadata
        self.geometry("600x600")
        self.title("Turtle Tennis - Image Manager")
        self.transient(parent)
        self.grid_rowconfigure(0, weight=2, uniform="uniform")
        self.grid_rowconfigure(1, weight=4, uniform="uniform")
        self.grid_rowconfigure(2, weight=1, uniform="uniform")
        self.grid_rowconfigure(3, weight=3, uniform="uniform")
        self.grid_columnconfigure(0, weight=3, uniform="uniform")
        self.grid_columnconfigure(1, weight=4, uniform="uniform")
        self.grid_columnconfigure(2, weight=3, uniform="uniform")

        # Widgets
        heading_label = cWidget.Label(self,
                                      fg_color=colours.get_primary_colour(),
                                      text="Product Image",
                                      font=("Poppins Regular", 48))
        heading_label.grid(row=0, column=0, columnspan=3, sticky="NS")

        self.current_image_display = cWidget.Frame(self, border_width=1)
        self.current_image_display.grid(row=1, column=1, sticky="NSEW")
        self.current_image_display.grid_rowconfigure(0, weight=1)
        self.current_image_display.grid_columnconfigure(0, weight=1)

        self.info_message = cWidget.Label(self,
                                          fg_color=colours.get_primary_colour(),
                                          font=("Inter Regular", 20))
        self.info_message.grid(row=2, column=0, pady=10, columnspan=3, sticky="N")

        # If there is no existing image
        if existing_image_file == "":
            self.current_image = None
            self.info_message.configure(text="Status: No image for our turtles to admire.")
            cWidget.FilledButton(self.current_image_display,
                                 bg_color=colours.get_bg_colour(),
                                 text="Choose image",
                                 command=lambda: self.prompt_for_image()).grid(row=0, column=0)
        else:
            # Place the existing image in the image holder
            self.current_image = existing_image_file
            self.info_message.configure(text="Status: Our turtles are admiring your image.")
            cWidget.Label(self.current_image_display,
                          image_file=existing_image_file,
                          image_width=100,
                          image_height=100).grid(row=0, column=0, padx=2, pady=2, sticky="NSEW")

        button_frame = cWidget.Frame(self, fg_color=colours.get_primary_colour())
        button_frame.grid(row=3, column=1, sticky="NSEW")
        button_frame.grid_rowconfigure(0, weight=1, uniform="uniform")
        button_frame.grid_rowconfigure(1, weight=1, uniform="uniform")
        button_frame.grid_columnconfigure(0, weight=1)
        delete_button = cWidget.FilledButton(button_frame,
                                             text="Change image",
                                             command=lambda: self.prompt_for_image())
        delete_button.grid(row=0, column=0, pady=10, sticky="S")
        confirm_button = cWidget.FilledButton(button_frame,
                                              text="Confirm",
                                              command=lambda: self.confirm_choice())
        confirm_button.grid(row=1, column=0, pady=10, sticky="N")

    def prompt_for_image(self):
        """
        Prompts the user to select an image
        """
        # Only prompt for .png and .jpg images
        image_request = askopenfilename(title="File explorer",
                                        filetypes=[("PNG File", "*.png"), ("JPG File", "*.jpg")],
                                        initialdir=backend.get_root_directory())
        # If user selected an image
        if image_request:
            for widget in self.current_image_display.winfo_children():
                widget.destroy()
            self.current_image = image_request
            self.info_message.configure(text="Status: Our turtles are admiring your image.")
            cWidget.Label(self.current_image_display,
                          image_file=image_request,
                          image_width=100,
                          image_height=100).grid(row=0, column=0, padx=2, pady=2, sticky="NSEW")
        else:
            # If no image is already in the image holder
            if not self.current_image:
                for widget in self.current_image_display.winfo_children():
                    widget.destroy()
                self.info_message.configure(text="Status: Search 'image' on Google if you are stuck.")
                cWidget.FilledButton(self.current_image_display,
                                     text="Choose image",
                                     bg_color=colours.get_bg_colour(),
                                     command=lambda: self.prompt_for_image()).grid(row=0, column=0)

    def confirm_choice(self):
        """
        Confirms that the image in the image holder is the desired image
        """
        # If there is an image in the image holder
        if self.current_image:
            self.destroy()
        else:
            mbox.showerror("Error!", "Image invalid")

    def get_choice(self):
        """
        Return the image in the image holder

        Returns
        -------
        str
            The file path of the image
        """
        return self.current_image
