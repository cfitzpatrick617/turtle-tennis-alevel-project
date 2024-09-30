# Built-in libraries
import socket
import timeit
from datetime import datetime, timedelta
import math
from matplotlib.figure import Figure
from mpl_toolkits.axisartist.axislines import Subplot
import os
from PIL import ImageTk, Image, ImageDraw, ImageFont
import textwrap

# External libraries
import customtkinter as ctk
from fpdf import FPDF
import yagmail

# Custom libraries
import backend
import crud_functionality as crud
import utilities as util
import validation

# Display settings
colours = util.Colours()


def get_should_encrypt():
    with open("encryption_status.txt", "r") as encryption_config:
        try:
            if encryption_config.readline()[0] == "1":
                return True
            else:
                return False
        except TypeError:
            raise Exception("""APPLICATION STOPPED: Encryption status has not been setup right.
            Please check the README for encryption setup.""")


def update_product_rating(product_id: int):
    """
    Update the average rating for a product

    Parameters
    ----------
    product_id : int
        The id of the product to get the average rating for
    """
    # Get the scores of all the ratings related to the product
    ratings = crud.search_table("ecommerce",
                                "Ratings",
                                ["score"],
                                f"product_id = '{product_id}'")
    scores = [rating.get("score") for rating in ratings]
    if len(scores) == 0:
        crud.update_record("ecommerce", "Product", {"average_rating": 0}, f"product_id = '{product_id}'")
    else:
        total = sum(scores)
        # Calculate the average (amount / count)
        crud.update_record("ecommerce",
                           "Product",
                           {"average_rating": round(total / len(scores), 1)},
                           f"product_id = '{product_id}'")


def count_ratings(product_id: int):
    """
    Count the number of ratings that exist for a product

    Parameters
    ----------
    product_id : int
        The id of the product

    Returns
    -------
    int
        The total number of ratings that exist
    """
    ratings = crud.search_table("ecommerce",
                                "Ratings",
                                ["score"],
                                f"product_id = '{product_id}'")
    return len(ratings)


def calculate_subtotal(basket: list):
    """
    Calculate the subtotal of a basket

    Parameters
    ----------
    basket : list
        A list of dictionaries which hold attributes of products within the basket

    Returns
    -------
    int | float
        The calculated subtotal
    """
    subtotal = 0
    for product in basket:
        subtotal += product.get("sale_price")*product.get("quantity")
    return subtotal


def clear_entry_widgets(entry_widget_list: list):
    """
    Clears a set of entry widgets and moves the cursor to the first widget

    Parameters
    ----------
    entry_widget_list : list
        The list of entry widget objects
    """
    for entry_widget in entry_widget_list:
        entry_widget.clear()
    entry_widget_list[0].focus_set()


def check_access(access_level: str,
                 table_name: str,
                 mode: str):
    """
    Checks whether a certain staff member can access a particular table for a particular mode

    Parameters
    ----------
    access_level : str
        The user's level of access, either 'Management' or 'Sales'

    table_name : str
        The name of the table which the user is trying to access

    mode : str
        The mode that the user wants to use, either:
            - C: Create
            - S: Search
            - U: Update
            - D: Delete 
    """
    if access_level == "Management":
        permitted_access = {"Customer": "CSUD",
                            "Staff": "CSUD",
                            "Orders": "SUD",
                            "Payment_Card": "SD",
                            "Product": "CSUD",
                            "Supplier": "CSUD",
                            "Ratings": "SD"}
    else:
        permitted_access = {"Customer": None,
                            "Staff": None,
                            "Orders": "S",
                            "Payment_Card": None,
                            "Product": "S",
                            "Supplier": None,
                            "Ratings": "S"}

    # If the user cannot access the table or cannot access a specific mode for a table
    if not permitted_access.get(table_name) or mode.upper() not in permitted_access.get(table_name):
        return False
    else:
        return True


def convert_field_name_style(field_name):
    """
    Convert raw database field names into aesthetically pleasing output

    Parameters
    ----------
    field_name : str
        The name of the raw database field
    """
    if field_name[-2:] == "id":
        return (field_name[:-2].replace("_", " ")).title() + "ID:"
    else:
        if field_name.lower() == "cvc":
            return "CVC:"
        else:
            return (field_name.replace("_", " ")).title() + ":"


def get_root_directory():
    """
    Get the path of the project's directory

    Returns
    -------
    str
        The file path of the directory
    """
    # Get the current path
    path = os.getcwd()
    return f"{os.path.dirname(path)}\\{os.path.basename(path)}\\"


def get_directory(directory_name: str = ""):
    """
    Gets the path of a directory for the application

    Parameters
    ----------
    directory_name : str
        The name of the directory

    Returns
    -------
    str
        The file path of the directory
    """
    directory = f"{get_root_directory()}{directory_name}\\"
    # Create directory if it does not exist
    if not os.path.exists(directory):
        os.mkdir(directory)
    return directory


def get_report_directory(report_name: str):
    """
    Gets the path of a directory within the 'reports' directory

    Parameters
    ----------
    report_name : str
        The name of the report directory

    Returns
    -------
    str
        The file path of the directory
    """
    parent_directory = get_directory("reports")
    report_directory = parent_directory + f"{report_name}\\"
    # Create directory if it does not exist
    if not os.path.exists(report_directory):
        os.mkdir(report_directory)
    return report_directory


def backup(database_name: str):
    """
    Backup the database

    Parameters
    ----------
    database_name : str
        The name of the database
    """
    date_created = datetime.now().strftime("%d-%m-%y")
    # Ensure the backups directory exists
    _ = get_directory("backups")
    new_file_path = f"backups\\{database_name}_backup_{date_created}.db"
    os.system(f"copy {database_name}.db {new_file_path}")
    print(f"BACKUP CREATED FOR {date_created}")


def get_recent_backup(database_name: str):
    """
    Get the most recent backup of the database

    Parameters
    ----------
    database_name: str
        The name of the database

    Returns
    -------
    list
        The backup's file name and the date it was created
    """
    # Get all file names and dates the files were last modified
    files = []
    for file_name in os.listdir(get_directory("backups")):
        file = {"file_name": file_name,
                "date_created": datetime.strptime(file_name[len(database_name) + 8:-3], "%d-%m-%y")}
        files.append(file)
    # Sort files so that the most recently modified one (i.e. the most recent backup) is first
    sorted_files_by_date = sorted(files, key=lambda file: file["date_created"], reverse=True)
    # Return list containing name and date of first (i.e. index 0) backup as previous list is sorted by most recent
    if sorted_files_by_date:
        return [list(sorted_files_by_date[0].values())[0],
                list(sorted_files_by_date[0].values())[1].strftime("%d-%m-%y")]
    else:
        return [None, None]


def create_report_header(pdf,
                         title: str):
    """
    Creates the template for the header of any summary report

    Parameters
    ----------
    pdf : FPDF obj
        The FPDF object created for the summary report

    title : str
        The title of the summary report

    Returns
    -------
    int
        The height of the header
    """
    # Load custom font
    pdf.add_font(fname="Poppins-Regular.ttf")
    pdf.set_font("Poppins-Regular", size=32)

    # Set draw colour and fill colour for the yellow rectangle (header background)
    pdf.set_draw_color(r=255, g=225, b=86)
    pdf.set_fill_color(r=255, g=225, b=86)
    header_h = 60
    # Create rectangle and set style to fill and bordered
    pdf.rect(0, 0, pdf.w, header_h, style="FD")
    # Place text in the vertical middle of the header
    pdf.set_y(header_h/2-(header_h/10))
    pdf.cell(w=40, txt=title)
    # Place image in the vertical middle of the header and with the same marginal spacing
    image_file = get_directory("images") + "turtle_tennis_icon_ICON_AND_TEXT.png"
    img_w = 40
    img_h = 40
    try:
        pdf.image(image_file, w=img_w, h=img_h, x=pdf.w-img_w-10, y=(header_h/2)-(img_h/2))
    except FileNotFoundError:
        image_file = get_directory("images") + "placeholder.png"
        pdf.image(image_file, w=img_w, h=img_h, x=pdf.w - img_w - 10, y=(header_h / 2) - (img_h / 2))

    return header_h


def create_comparison_report(product_one: dict,
                             product_two: dict):
    """
    Creates the product comparison summary report for the Customer stakeholder

    Parameters
    ----------
    product_one : dict
        The first product for comparison.
        Keys should state the product attribute names.
        Values should state the attribute values

    product_two : dict
        The second product for comparison.
        Keys should state the product attribute names.
        Values should state the attribute values

    Returns
    -------
    str
        The file name for the product comparison pdf created
    """
    pdf = FPDF()
    pdf.add_page()
    header_h = create_report_header(pdf, title="Product Comparison")

    column_one_width = pdf.epw * 0.2
    other_columns_width = pdf.epw * 0.4
    pdf.set_xy(10, header_h+5)

    image_width = 60
    image_height = 60
    image_file_one = product_one.get("image_file")
    pdf.set_x(10+column_one_width+((other_columns_width-image_width)/2))
    try:
        pdf.image(image_file_one,
                  w=image_width,
                  h=image_height)
    except FileNotFoundError:
        # Replace image with a placeholder instead
        image_file_one = get_directory("images") + "placeholder.png"
        pdf.image(image_file_one,
                  w=image_width,
                  h=image_height)
    image_file_two = product_two.get("image_file")
    pdf.set_xy(10+column_one_width+other_columns_width+((other_columns_width-image_width)/2), header_h+5)
    try:
        pdf.image(image_file_two,
                  w=image_width,
                  h=image_height)
    except FileNotFoundError:
        # Replace image with a placeholder instead
        image_file_two = get_directory("images") + "placeholder.png"
        pdf.image(image_file_two,
                  w=image_width,
                  h=image_height)

    # Split description into 18-character maximum lines
    formatted_description_one = textwrap.fill(text=product_one.get("description"), width=18)
    formatted_description_two = textwrap.fill(text=product_two.get("description"), width=18)
    # If description one has more line breaks than description two
    if formatted_description_one.count("\n") > formatted_description_two.count("\n"):
        max_num_lines = formatted_description_one.count("\n") + 1
        # Add line breaks to fill the gap in lines between description two and description one
        formatted_description_two += ("\n " * (max_num_lines - 1 - formatted_description_two.count("\n")))
    # If description two has more line breaks than description one OR they have an equal amount of lines
    else:
        max_num_lines = formatted_description_two.count("\n") + 1
        # Add any line breaks needed to fill the gap in lines between description one and two
        formatted_description_one += ("\n " * (max_num_lines - 1 - formatted_description_one.count("\n")))

    pdf.set_xy(10, pdf.get_y()+5)
    top_of_table = pdf.get_y()
    pdf.set_draw_color(r=0, g=0, b=0)
    pdf.set_fill_color(r=255, g=225, b=86)
    pdf.add_font(fname="Inter-Regular.ttf")
    pdf.ln()

    left_margin = 10
    row_height = 20
    # Reset to left side of column and the top of the table
    pdf.set_xy(left_margin, top_of_table)
    pdf.set_fill_color(r=255, g=225, b=86)
    pdf.set_font("Poppins-Regular", size=16)
    pdf.cell(w=column_one_width, h=row_height, border=1, fill=True)
    pdf.cell(w=other_columns_width, h=row_height, txt=product_one.get("name"), border=1, fill=True, align="C")
    pdf.cell(w=other_columns_width, h=row_height, txt=product_two.get("name"), border=1, fill=True, align="C")

    def display_subheading(text: str):
        """
        Displays a subheading on the PDF

        Parameters
        ----------
        text : str
            The text used for the subheading
        """
        pdf.set_fill_color(r=255, g=225, b=86)
        pdf.set_font("Poppins-Regular", size=16)
        if text == "Description":
            # Calculate which line number is center line
            center_line = math.floor((max_num_lines + 1) / 2)
            # Add line breaks for any lines before the center
            lines_before = "\n" * (center_line-1)
            # Add line breaks for any lines after the center
            lines_after = "\n " * (max_num_lines - center_line)
            # Essentially manually centers the text
            formatted_description_heading = f"{lines_before}Description{lines_after}"
            pdf.multi_cell(w=column_one_width,
                           txt=formatted_description_heading,
                           border=1,
                           fill=True,
                           align="C")
            pdf.set_xy(10+column_one_width, top_of_description)
        else:
            pdf.cell(w=column_one_width, h=row_height, txt=text, border=1, fill=True, align="C")

    # Reset to next line and left side of column
    pdf.ln()
    pdf.set_x(left_margin)
    # Display categories
    display_subheading("Category")
    pdf.set_font("Inter-Regular", size=16)
    pdf.cell(w=other_columns_width, h=row_height, txt=product_one.get("category"), border=1, align="C")
    pdf.cell(w=other_columns_width, h=row_height, txt=product_two.get("category"), border=1, align="C")

    # Reset to next line and left side of column
    pdf.ln()
    pdf.set_x(left_margin)
    # Display unit prices
    display_subheading("Price")
    pdf.set_fill_color(r=255, g=255, b=255)
    pdf.set_font("Inter-Regular", size=16)
    price_one = product_one.get("sale_price")
    pdf.cell(w=other_columns_width, h=row_height, txt=f"£{price_one:.2f}", border=1, align="C")
    price_two = product_two.get("sale_price")
    pdf.cell(w=other_columns_width, h=row_height, txt=f"£{price_two:.2f}", border=1, align="C")

    # Reset to next line and left side of column
    pdf.ln()
    pdf.set_x(left_margin)
    top_of_description = pdf.get_y()
    # Display descriptions
    display_subheading("Description")
    pdf.set_fill_color(r=255, g=255, b=255)
    pdf.set_font("Inter-Regular", size=16)
    pdf.multi_cell(w=other_columns_width,
                   txt=formatted_description_one,
                   border=1,
                   align="C")
    pdf.set_xy(10+column_one_width+other_columns_width,
               top_of_description)
    pdf.multi_cell(w=other_columns_width,
                   txt=formatted_description_two,
                   border=1,
                   align="C")

    # Leave out ln() here as it breaks multi_cell
    # Reset to left side of column
    pdf.set_x(left_margin)
    # Display ratings
    display_subheading("Rating")
    pdf.set_fill_color(r=255, g=255, b=255)
    pdf.set_font("Inter-Regular", size=16)
    rating_one = product_one.get("average_rating")
    pdf.cell(w=other_columns_width, h=row_height, txt=f"{rating_one:.1f}", border=1, align="C")
    rating_two = product_two.get("average_rating")
    pdf.cell(w=other_columns_width, h=row_height, txt=f"{rating_two:.1f}", border=1, align="C")

    # Reset to next line and left side of column
    pdf.ln()
    pdf.set_x(left_margin)
    # Display supplier
    display_subheading("Supplier")
    pdf.set_fill_color(r=255, g=255, b=255)
    pdf.set_font("Inter-Regular", size=16)
    pdf.cell(w=other_columns_width, h=row_height, txt=product_one.get("company_name"), border=1, align="C")
    pdf.cell(w=other_columns_width, h=row_height, txt=product_two.get("company_name"), border=1, align="C")

    # Time and date integrated into file names to avoid clashing file names
    now = datetime.now()
    current_date_and_time = now.strftime("%d-%m-%y_%H-%M-%S")
    # Create pdf document and save to application folder
    file_name = f"{get_report_directory('product_comparison')}product_comparison_{current_date_and_time}.pdf"
    pdf.output(name=file_name)
    
    return file_name


def create_receipt(order_id: int,
                   full_name: str):
    """
    Creates a receipt of a past order for the Customer and Management Staff stakeholders

    Parameters
    ----------
    order_id : int
        The ID for the order

    full_name : str
        The full name of the customer who created the order

    Returns
    -------
    str
        The file name for the receipt pdf created
    """
    pdf = FPDF()
    pdf.add_page()
    header_h = create_report_header(pdf, title="Order Receipt")

    # Get order details from database
    order = crud.search_joined_table("ecommerce",
                                     "Orders",
                                     [["Payment_Card", "payment_card_id"]],
                                     ["*"],
                                     f"order_id='{order_id}'")[0]
    products_in_order = crud.search_joined_table("ecommerce",
                                                 "Order_Product",
                                                 [["Product", "product_id"]],
                                                 ["name",
                                                  "sale_price",
                                                  "quantity"],
                                                 f"order_id = '{order_id}'")
                                          
    # Display customer information
    pdf.set_xy(10, header_h+15)
    pdf.set_font("Poppins-Regular", size=16)
    pdf.set_text_color(r=128, g=128, b=128)
    pdf.cell(w=40, txt="Billed to")
    pdf.ln()
    pdf.add_font(fname="Inter-Regular.ttf")
    pdf.set_font("Inter-Regular", size=20)
    pdf.set_text_color(r=0, g=0, b=0)
    card_num = order.get("card_number")
    pdf.multi_cell(w=pdf.epw*0.75, txt=f"{full_name}\nXXXX XXXX XXXX {card_num[-4:]}")

    # Display delivery information
    pdf.ln()
    pdf.set_x(10)
    pdf.set_font("Poppins-Regular", size=16)
    pdf.set_text_color(r=128, g=128, b=128)
    pdf.cell(w=40, txt="Delivered to")
    pdf.ln()
    pdf.set_x(10)
    pdf.set_font("Inter-Regular", size=20)
    pdf.set_text_color(r=0, g=0, b=0)
    address = order.get("delivery_address")
    postcode = order.get("delivery_postcode")
    pdf.multi_cell(w=80, txt=f"{address}\n{postcode}")

    # Display order information
    pdf.set_xy(-50, header_h+15)
    pdf.set_font("Poppins-Regular", size=16)
    pdf.set_text_color(r=128, g=128, b=128)
    pdf.cell(w=40, txt="Order Number", align="R")
    pdf.ln()
    pdf.set_x(-50)
    pdf.set_font("Inter-Regular", size=20)
    pdf.set_text_color(r=0, g=0, b=0)
    pdf.multi_cell(w=40, txt=f"{order_id}\n", align="R")
    pdf.ln()
    pdf.set_x(-50)
    pdf.set_font("Poppins-Regular", size=16)
    pdf.set_text_color(r=128, g=128, b=128)
    pdf.cell(w=40, txt="Date of Order", align="R")
    pdf.ln()
    pdf.set_x(-50)
    pdf.set_font("Inter-Regular", size=20)
    pdf.set_text_color(r=0, g=0, b=0)
    date = order.get("date")
    pdf.cell(w=40, txt=f"{date}", align="R")

    # Display table of products bought
    pdf.ln(30)
    pdf.set_x(10)
    pdf.set_draw_color(r=0, g=0, b=0)
    pdf.set_fill_color(r=255, g=225, b=86)
    headings = ["Product", "Unit cost", "Quantity", "Total cost"]

    # Divide the space in between the page margins into equal width
    column_width = pdf.epw/6
    row_height = 15
    pdf.set_font("Poppins-Regular", size=16)
    # Display table headings
    for heading in headings:
        if heading == "Product":
            pdf.cell(w=column_width*3, h=row_height, txt=heading, border=1, fill=True, align="C")
        else:
            pdf.cell(w=column_width, h=row_height, txt=heading, border=1, fill=True, align="C")
    pdf.set_font("Inter-Regular", size=20)
    # Display products in a row by row fashion
    for product in products_in_order:
        pdf.ln()
        sale_price = product.get("sale_price")
        quantity = product.get("quantity")
        total_cost = sale_price * quantity
        pdf.cell(w=column_width*3, h=row_height, txt=product.get("name"), border=1, align="C")
        pdf.cell(w=column_width, h=row_height, txt=f"£{sale_price:.2f}", border=1, align="C")
        pdf.cell(w=column_width, h=row_height, txt=str(quantity), border=1, align="C")
        pdf.cell(w=column_width, h=row_height, txt=f"£{total_cost:.2f}", border=1, align="C")

    # Display costs
    pdf.ln(30)
    x_alignment = pdf.epw/2+10
    row_height = 8
    column_width = pdf.epw/4
    
    subheadings = ["Subtotal", "Delivery cost", "Total"]
    total = order.get("total_cost")
    del_cost = order.get("delivery_cost")
    subtotal = total - del_cost
    data = [f"£{subtotal:.2f}", f"£{del_cost:.2f}", f"£{total:.2f}"]
    pdf.set_draw_color(r=255, g=225, b=86)
    # Display subtotal, delivery cost and total in a row by row fashion
    for count, subheading in enumerate(subheadings):
        # For the final field i.e. the total
        if count == len(subheadings)-1:
            # Place a yellow background with a border
            fill = True
            border = 1
        else:
            fill = False
            border = 0
        pdf.set_x(x_alignment)
        pdf.set_font("Poppins-Regular", size=16)
        pdf.cell(w=column_width, h=row_height, txt=subheading, fill=fill, border=border)
        pdf.set_font("Inter-Regular", size=20)
        pdf.cell(w=column_width, h=row_height, txt=data[count], fill=fill, border=border, align="R")
        pdf.ln()

    # Time and date integrated into file names to avoid clashing file names
    now = datetime.now()
    current_date_and_time = now.strftime("%d-%m-%y_%H-%M-%S")
    # Create pdf document and save to application folder
    file_name = f"{get_report_directory('receipts')}order{order_id}_{current_date_and_time}.pdf"
    pdf.output(name=file_name)

    return file_name


def get_total_sold(product_id: int, days_considered: int):
    """
    Get the total units sold for a product over a past number of days

    Parameters
    ----------
    product_id : int
        The ID of the product

    days_considered : int
        The number of past days the data should be from

    Returns
    -------
    int
        The total units sold
    """
    # Calculate timeframe
    end_of_timeframe = datetime.today()
    start_of_timeframe = datetime.today() - timedelta(days=days_considered)

    # Calculate sales data between timeframe
    orders = crud.search_table("ecommerce",
                               "Orders",
                               ["*"],
                               f"date >= '{start_of_timeframe.strftime('%Y-%m-%d')}' AND date <= '{end_of_timeframe.strftime('%Y-%m-%d')}'")
    order_ids = [f"'{order.get('order_id')}'" for order in orders]
    formatted_order_ids = ", ".join(order_ids)

    orders_with_product = crud.search_table("ecommerce",
                                            "Order_Product",
                                            ["*"],
                                            f"order_id in ({formatted_order_ids}) AND product_id = '{product_id}'")
    # Tally all the units sold for each order
    return sum([order_with_product.get("quantity") for order_with_product in orders_with_product])


def create_product_summary(product_id: int, days_back: int):
    """
    Creates a report of a product's performance over a past number of days

    Parameters
    ----------
    product_id : int
        The ID for the product

    days_back : int
        The number of past days the data should be from

    Returns
    -------
    str
        The file name for the report pdf created
    """
    pdf = FPDF()
    pdf.add_page()
    header_h = create_report_header(pdf, title="Product performance")

    product = crud.search_table("ecommerce",
                                "Product",
                                ["*"],
                                f"product_id = '{product_id}'")[0]

    # Calculate timeframe
    end_of_timeframe = datetime.today()
    start_of_timeframe = datetime.today() - timedelta(days=days_back)
    timeframe = f"{start_of_timeframe.strftime('%d/%m/%y')} - {end_of_timeframe.strftime('%d/%m/%y')}"

    # Get sales data
    total_sold = get_total_sold(product_id, days_back)
    total_revenue = total_sold * product.get("sale_price")
    total_cogs = total_sold * product.get("order_cost")
    gross_profit = total_revenue - total_cogs
    # Avoid runtime error by checking it will not divide by 0
    if total_revenue != 0:
        gross_profit_margin = round(gross_profit / total_revenue, 2)
    else:
        gross_profit_margin = "N/A"

    # Display product information
    pdf.set_xy(10, header_h + 15)
    pdf.set_font("Poppins-Regular", size=16)
    pdf.set_text_color(r=128, g=128, b=128)
    pdf.cell(w=40, txt="Product ID")
    pdf.ln()
    pdf.add_font(fname="Inter-Regular.ttf")
    pdf.set_font("Inter-Regular", size=20)
    pdf.set_text_color(r=0, g=0, b=0)
    pdf.cell(w=40, txt=f"{product_id}")
    pdf.ln(20)
    pdf.set_x(10)
    pdf.set_font("Poppins-Regular", size=16)
    pdf.set_text_color(r=128, g=128, b=128)
    pdf.cell(w=40, txt="Product name")
    pdf.ln()
    pdf.set_x(10)
    pdf.set_font("Inter-Regular", size=20)
    pdf.set_text_color(r=0, g=0, b=0)
    pdf.cell(w=40, txt=f"{product.get('name')}")

    pdf.set_xy(-80, header_h + 15)
    pdf.set_font("Poppins-Regular", size=16)
    pdf.set_text_color(r=128, g=128, b=128)
    pdf.cell(w=70, txt="Data collected from", align="R")
    pdf.ln()
    pdf.set_x(-50)
    pdf.set_font("Inter-Regular", size=20)
    pdf.set_text_color(r=0, g=0, b=0)
    pdf.cell(w=40, txt=f"{timeframe}", align="R")
    pdf.ln(20)
    pdf.set_x(-80)
    pdf.set_font("Poppins-Regular", size=16)
    pdf.set_text_color(r=128, g=128, b=128)
    pdf.cell(w=70, txt="Gross profit margin", align="R")
    pdf.ln()
    pdf.set_x(-50)
    pdf.set_font("Inter-Regular", size=20)
    pdf.set_text_color(r=0, g=0, b=0)
    pdf.cell(w=40, txt=f"{gross_profit_margin}", align="R")

    pdf.set_x(10)
    pdf.ln(20)
    pdf.set_draw_color(r=0, g=0, b=0)
    headings = {"Units sold": total_sold,
                "Sale price": product.get("sale_price"),
                "Total revenue": total_revenue,
                "Total cost": total_cogs,
                "Gross profit": gross_profit}
    # Divide the space in between the page margins into equal width
    column_width = pdf.epw / 5
    row_height = 15
    top_of_table = pdf.get_y()
    # Display table headings
    for count, (heading, value) in enumerate(headings.items()):
        pdf.set_xy(10+(column_width*count), top_of_table)
        pdf.set_font("Poppins-Regular", size=16)
        pdf.set_fill_color(r=255, g=225, b=86)
        pdf.cell(w=column_width, h=row_height, txt=heading, border=1, fill=True, align="C")
        pdf.ln()
        pdf.set_x(10+(column_width*count))
        pdf.set_font("Inter-Regular", size=16)
        if heading != "Units sold":
            # Format currency to 2 d.p
            value_to_display = f"£{value:.2f}"
        else:
            value_to_display = str(value)
        pdf.cell(w=column_width, h=row_height, txt=value_to_display, border=1, align="C")

    # Get rating data
    ratings = crud.search_table("ecommerce",
                                "Ratings",
                                ["*"],
                                f"product_id = {product_id} AND date >= '{start_of_timeframe.strftime('%Y-%m-%d')}' AND date <= '{end_of_timeframe.strftime('%Y-%m-%d')}'")
    scores = [rating.get("score") for rating in ratings]
    scores_grouped = {f"{count} star": scores.count(count) for count in range(1, 6)}
    num_of_ratings = len(scores)
    # Avoid runtime error by checking it will not divide by 0
    if num_of_ratings != 0:
        average_rating = sum(scores) / num_of_ratings
    else:
        average_rating = "N/A"

    pdf.ln(30)
    pdf.set_x(10)
    pdf.set_font("Poppins-Regular", size=16)
    pdf.set_text_color(r=128, g=128, b=128)
    pdf.cell(w=40, txt="Number of ratings")
    pdf.set_x(-50)
    pdf.cell(w=40, txt="Average rating", align="R")
    pdf.ln()
    pdf.set_font("Inter-Regular", size=20)
    pdf.set_text_color(r=0, g=0, b=0)
    pdf.cell(w=40, txt=f"{num_of_ratings}")
    pdf.set_x(-50)
    pdf.cell(w=40, txt=f"{average_rating}", align="R")

    pdf.ln(20)
    pdf.set_x(10)
    pdf.set_font("Poppins-Regular", size=16)
    pdf.set_text_color(r=128, g=128, b=128)
    pdf.cell(w=80, txt="Composition of ratings")

    # Create pie chart and display pie chart
    pdf.ln()
    current_date_and_time = datetime.now().strftime("%d-%m-%y_%H-%M-%S")
    # If ratings exist
    if list(scores_grouped.values()).count(0) != 5:
        pdf.set_x(10 + pdf.epw / 3)
        # Create object of plt class to enable threading to work
        pie_labels = [f"{items[0]} ({items[1]})" for items in list(scores_grouped.items()) if items[1] != 0]
        pie_values = [items[1] for items in list(scores_grouped.items()) if items[1] != 0]
        fig = Figure()
        ax = Subplot(fig, 111)
        # Set border to be invisible
        ax.axis["left"].set_visible(False)
        ax.axis["top"].set_visible(False)
        ax.axis["right"].set_visible(False)
        ax.axis["bottom"].set_visible(False)
        fig.add_subplot(ax)
        # Create the pie chart
        ax.pie(pie_values, labels=pie_labels, startangle=90)
        # Save plot as a file, then enter the plot into the pdf by creating an image of that file
        pie_chart_file = f"{get_report_directory('plotted_figures')}ratings_pie_chart_{current_date_and_time}.png"
        fig.savefig(pie_chart_file, bbox_inches="tight")
        pdf.image(pie_chart_file, w=pdf.epw/3, h=60)
    else:
        pdf.set_x(10)
        pdf.set_font("Inter-Regular", size=20)
        pdf.set_text_color(r=0, g=0, b=0)
        # Display that no rating data was available
        pdf.cell(w=40, h=60, txt="N/A")

    # Time and date integrated into file names to avoid clashing file names
    current_date_and_time = datetime.now().strftime("%d-%m-%y_%H-%M-%S")
    # Create pdf document and save to application folder
    file_name = f"{get_report_directory('product_performance')}product{product_id}_{current_date_and_time}.pdf"
    pdf.output(name=file_name)

    return file_name


def decrypt(field_name, encrypted_field, override_encryption_status = False):
    """
    Decrypts the field using an ASCII version of the Vigenere cipher

    Parameters
    ----------
    encrypted_field : str
        The field to decrypt

    Returns
    -------
    str
        The decrypted field
    """
    do_not_decrypt_fields = ["customer_id",
                             "staff_id",
                             "weekly_hours",
                             "payment_card_id",
                             "order_id",
                             "date",
                             "delivery_cost",
                             "total_cost",
                             "supplier_id",
                             "current_stock",
                             "average_rating",
                             "order_cost",
                             "sale_price",
                             "total_sold",
                             "product_id",
                             "order_product_id",
                             "quantity",
                             "rating_id",
                             "score"]
    if field_name in do_not_decrypt_fields or (not get_should_encrypt() and not override_encryption_status):
        return encrypted_field
    else:
        plaintext_key = "pepsi_max"
        # Convert key into list of ASCII values
        key_ascii_values = [ord(character) for character in plaintext_key]

        table_range = [integer for integer in range(32, 127)]
        # Source: https://stackoverflow.com/questions/47369057/generate-vigen%C3%A8re-cypher-table-in-python
        vigenere_table = [table_range[i:] + table_range[:i] for i in range(len(table_range))]

        key_pointer = 0
        decrypted_field = ""
        for character in str(encrypted_field):
            column = key_ascii_values[key_pointer] - 32
            # Get the row where the column number is the ASCII value of the encrypted character
            row = [row for row in vigenere_table if row[column] == ord(character)]
            # Trace to start of said row (that will be the ASCII value of the decrypted character)
            decrypted_character = chr(row[0][0])
            if decrypted_character == "'" and not get_should_encrypt():
                # Change ' into '' to avoid SQL insertion errors
                decrypted_field += "''"
            else:
                decrypted_field += decrypted_character
            # If key has looped back to the beginning
            if key_pointer + 1 > len(key_ascii_values) - 1:
                key_pointer = 0
            else:
                key_pointer += 1

        return decrypted_field


def encrypt(field_name, decrypted_field, override_encryption_status = False):
    """
    Encrypts the field using an ASCII version of the Vigenere cipher

    Parameters
    ----------
    decrypted_field : str
        The field to encrypt

    Returns
    -------
    str
        The encrypted field
    """
    do_not_encrypt_fields = ["customer_id",
                             "staff_id"
                             "weekly_hours",
                             "payment_card_id",
                             "order_id",
                             "date",
                             "delivery_cost",
                             "total_cost",
                             "supplier_id",
                             "current_stock",
                             "average_rating",
                             "order_cost",
                             "sale_price",
                             "total_sold",
                             "product_id",
                             "order_product_id",
                             "quantity",
                             "rating_id",
                             "score"]
    if field_name in do_not_encrypt_fields or (not get_should_encrypt() and not override_encryption_status):
        return str(decrypted_field)
    else:
        plaintext_key = "pepsi_max"
        # Convert key into list of ASCII values
        key_ascii_values = [ord(character) for character in plaintext_key]

        # Starts at 32 and not 0 as ASCII values 0 - 32 are unusable
        table_range = [integer for integer in range(32, 127)]
        # Source: https://stackoverflow.com/questions/47369057/generate-vigen%C3%A8re-cypher-table-in-python
        vigenere_table = [table_range[i:] + table_range[:i] for i in range(len(table_range))]

        key_pointer = 0
        encrypted_field = ""
        for character in decrypted_field:
            row = ord(character) - 32
            # Column is detemined by the current key character value
            column = key_ascii_values[key_pointer] - 32
            # VISUAL REPRESENTATION OF WHAT IS HAPPENING CAN BE FOUND IN DESIGN DOCUMENTS
            encrypted_character = chr(vigenere_table[row][column])
            if encrypted_character == "'" and get_should_encrypt():
                # Change ' into '' to avoid SQL insertion errors
                encrypted_field += "''"
            else:
                encrypted_field += encrypted_character
            # If key has looped back to beginning
            if key_pointer + 1 > len(key_ascii_values)-1:
                key_pointer = 0
            else:
                key_pointer += 1

        return encrypted_field


def encrypt_all():
    tables = ["Customer", "Order_Product", "Orders", "Payment_Card", "Product", "Ratings", "Staff", "Supplier"]
    for table_name in tables:
        records = crud.search_table("ecommerce", table_name, "*", "")
        for record in records:
            new_record = {}
            for field_name, value in record.items():
                if field_name[-2:] != "id":
                    new_record[field_name] = backend.encrypt(field_name, value, override_encryption_status=True)
            id_name, id_value = list(record.items())[0]
            crud.update_record("ecommerce",
                               table_name,
                               new_record,
                               f"{id_name} = '{id_value}'")


def decrypt_all():
    tables = ["Customer", "Order_Product", "Orders", "Payment_Card", "Product", "Ratings", "Staff", "Supplier"]
    for table_name in tables:
        records = crud.search_table("ecommerce", table_name, "*", "")
        for record in records:
            new_record = {}
            for field_name, value in record.items():
                if field_name[-2:] != "id":
                    new_record[field_name] = backend.decrypt(field_name, value, override_encryption_status=True)
            print(new_record)
            id_name, id_value = list(record.items())[0]
            crud.update_record("ecommerce",
                               table_name,
                               new_record,
                               f"{id_name} = '{id_value}'")


def decrease_stock_by(product_id: int,
                      amount: int = 1):
    """
    Decreases the current stock of an item by a certain amount

    Parameters
    ----------
    product_id : int
        The id of the product which should have its stock decreased

    amount : int
        The amount by which the stock should decrease by.
        Defaults to 1
    """
    current_stock = crud.search_table("ecommerce",
                                      "Product",
                                      ["current_stock"],
                                      f"product_id = '{product_id}'")[0].get("current_stock")
    crud.update_record("ecommerce",
                       "Product",
                       {"current_stock": current_stock - amount},
                       f"product_id = '{product_id}'")


def filter_products(products: list,
                    checkboxes_dict: dict,
                    minimum_rating: float,
                    need_in_stock: int):
    """
    Applies all applied browsing filters to a set of products and returns any matches

    Parameters
    ----------
    products : list
        A list of dictionaries which hold information about the original product set.
        Keys should state the field names.
        Values should state the corresponding field values

    checkboxes_dict : dict
        A dictionary of checkbox objects that are used for filtering by product.
        Keys should state the category name.
        Values should state the checkbox object

    minimum_rating : float
        The value of the minimum rating filter

    need_in_stock : int
        A value used to indicate if the products have to be in stock.
        The value will be 1 if the product must be in stock and 0 if not

    Returns
    -------
    list
        A list of dictionaries of products which match the filters applied
    """
    new_products = []
    if need_in_stock:
        min_stock = 0
    else:
        # Set the minimum stock to a value where any value entered will be greater
        min_stock = -999

    valid_category_names = []
    # Get the states of all the checkboxes
    checkbox_states = [checkbox.get() for checkbox in list(checkboxes_dict.values())]
    # If all checkboxes are off
    if checkbox_states.count("off") == len(list(checkboxes_dict.values())):
        # Then set all categories to be valid
        valid_category_names = [value for value in list(checkboxes_dict.keys())]
    else:
        for category_name, checkbox in checkboxes_dict.items():
            if checkbox.get() == "on":
                # Set that category to be valid
                valid_category_names.append(category_name)
    # Check fo products that match all criteria
    for product in products:
        if (
                product.get("category") in valid_category_names
                and product.get("average_rating") >= minimum_rating
                and product.get("current_stock") > min_stock
        ):
            new_products.append(product)
            
    return new_products


def create_placeholder():
    """
    Create placeholder image to replace a missing image
    """
    width = 100
    height = 100
    # Ensure the image is transparent
    image = Image.new("RGBA", (width, height), color=(255, 0, 0, 0))
    try:
        Image.open(get_directory("images") + "placeholder.png")
    # If placeholder does not exist
    except OSError:
        # Try to get complementary error image for the placeholder
        try:
            error_image = Image.open(get_directory("images") + "detective_turtle.png").resize((round(width/2), round(height/2)), Image.ANTIALIAS)
        except OSError:
            error_image = None
        pencil = ImageDraw.Draw(image)
        font = ImageFont.truetype("Inter-Regular.ttf", 10)
        text_w, text_h = pencil.textsize("Oops...\nNo image found.", font)
        if error_image:
            # Place text 20% down the image and in the horizontal center
            pencil.text((width/2-text_w/2, height*0.2-text_h/2),
                        "Oops...\nNo image found.",
                        (0, 0, 0),
                        font=font,
                        align="center")
            # Place image 40% down the image and in the horizontal center
            image.paste(error_image, (round(width/2 - width/4), round(height*0.4)))
        else:
            # Place text in middle
            pencil.text((width/2-text_w/2, height/2-text_h/2), "Oops...\nNo image found.", (0, 0, 0), font=font, align="center")
        file_path = get_directory("images") + "placeholder.png"
        image.save(file_path)


def load_and_resize_image(image_file: str,
                          width: int,
                          height: int):
    """
    Function used to initialise a PhotoImage object and
    resize it to specific dimensions

    Parameters
    ----------
    image_file : str
        The file name of the image which is to be loaded. Must contain file type

    width : int
        The desired width of the photo to be loaded. Measured in pixels

    height : int
        The desired height of the photo to be loaded. Measured in pixels

    Returns
    -------
    ctk.CTkImage
        The formatted CTkImage object with the desired dimensions applied
    """
    # Check to see if the image is external from the application images
    try:
        image = Image.open(f"{image_file}")
    except OSError:
        # Check to see if the image is an application image
        try:
            print(image_file)
            image = Image.open(get_directory("images") + f"{image_file}")
        # If image does not exist, replace it with the placeholder image
        except OSError:
            image = Image.open(get_directory("images") + "placeholder.png")

    return ctk.CTkImage(light_image=image,
                        dark_image=image,
                        size=(width, height))


def update_total_sold(product_id: int):
    """
    Update the total sold for a particular product

    Parameters
    ----------
    product_id : int
        The ID of the product
    """
    orders_with_product = crud.search_table("ecommerce",
                                            "Order_Product",
                                            ["*"],
                                            f"product_id = '{product_id}'")
    quantities_bought = [order.get("quantity") for order in orders_with_product]
    crud.update_record("ecommerce",
                       "Product",
                       {"total_sold": f"{sum(quantities_bought)}"},
                       f"product_id = {product_id}")
    

def process_order(user,
                  card_info: dict,
                  new_card_created: bool,
                  delivery_info: list):
    """
    Creates the payment card, order and linking table records for an order and sends a receipt via email

    Parameters
    ----------
    user : users.User
        A User object representing the user currently using the system

    card_info : dict
        A dictionary of card details that is being used as payment for the order.
        Keys should state the field names.
        Values should state the corresponding field values

    new_card_created : bool
        Whether a new card needs to be created
        The value will be True if a new card needs to be created and False if not

    delivery_info : list
        A list of delivery details that is being used for the order

    Returns
    -------
    list
        An integer for the id of the order created and a boolean value indicating
        whether the email was successfully sent
    """
    # Create card if a new card was entered
    if new_card_created:
        crud.add_record("ecommerce",
                        "Payment_Card",
                        card_info)
        payment_card_id = crud.search_table("ecommerce",
                                            "Payment_Card",
                                            ["*"],
                                            f"card_number = '{encrypt('card_number', card_info.get('card_number'))}'")[0].get("payment_card_id")
    else:
        payment_card_id = card_info.get("payment_card_id")

    basket = user.get_basket()
    customer_id = user.get_personal_id()

    # Get the current date
    date = datetime.today().strftime('%Y-%m-%d')
    del_cost = basket.get_delivery_cost()
    total_cost = basket.get_total()
    del_status = "Pending"

    order_dict = {"date": date,
                  "delivery_address": delivery_info.get("delivery_address"),
                  "delivery_postcode": delivery_info.get("delivery_postcode").upper(),
                  "delivery_cost": del_cost,
                  "total_cost": round(total_cost, 2),
                  "delivery_status": del_status,
                  "customer_id": customer_id,
                  "payment_card_id": payment_card_id}
    # Create order
    crud.add_record("ecommerce",
                    "Orders",
                    order_dict)

    # Get all order ids for the customer
    order_ids = crud.search_table("ecommerce",
                                  "Orders",
                                  ["order_id"],
                                  "")
    # Get the last order id as it must be the most recent order made
    order_id = order_ids[-1].get("order_id")

    for product in basket.get_products():
        order_product_dict = {"quantity": product.get("quantity"),
                              "product_id": product.get("product_id"),
                              "order_id": order_id}
        # Create linking table record for that product
        crud.add_record("ecommerce",
                        "Order_Product",
                        order_product_dict)
        # Update stock and total sold
        decrease_stock_by(order_product_dict.get("product_id"), order_product_dict.get("quantity"))
        update_total_sold(order_product_dict.get("product_id"))
    basket.reset_basket()

    name = user.get_name()
    surname = user.get_surname()
    # Generate receipt pdf
    receipt_file = create_receipt(order_id=order_id,
                                  full_name=f"{name} {surname}")

    # Send the email
    email_sent = send_email(user.get_email(),
                            subject="Your order receipt",
                            body_text=f"""Hi {name}, thanks for ordering with us!\nHere is a copy of your receipt. 
                            You can also view your past orders on the 'order history' section of our app!""",
                            attachments=[receipt_file])
    
    return [order_id, email_sent]


def remove_redundant_whitespace(string: str):
    """
    Removes instances of multiple whitespaces and new lines within
    a given piece of text

    Parameters
    ----------
    string : str
        The string to be formatted

    Returns
    -------
    str
        The formatted string
    """
    word_list = string.split(" ")
    non_whitespace_word_list = [word for word in word_list if word != "" and word != "\n"]
    return " ".join(non_whitespace_word_list)


def search_products(products: list,
                    search_value: str):
    """
    Search for a particular product in a set of products by a field

    Parameters
    ----------
    products : list
        A list of dictionaries which hold information about the original product set.
        Keys should state the field names.
        Values should state the corresponding field values

    search_value : str
        The search value

    Returns
    -------
    list
        A list of dictionaries of products which match the filters applied
    """
    new_products = []
    # Remove redundant whitespace
    stripped_search_value = backend.remove_redundant_whitespace(search_value)
    length_of_search = len(str(stripped_search_value))
    for product_dict in products:
        # Ensure the product attribute is in string format for comparison
        # Convert both values to uppercase as searches are not case-sensitive
        if (
                # Check if the search is the first part of the name, supplier or product id
                stripped_search_value.upper() == str(product_dict.get("name")).upper()[:length_of_search]
                or stripped_search_value.upper() == str(product_dict.get("company_name")).upper()[:length_of_search]
                or stripped_search_value.upper() == str(product_dict.get("product_id")).upper()[:length_of_search]
        ):
            new_products.append(product_dict)
    return new_products


def send_email(to_address: str,
               subject: str = "",
               body_text: str = "",
               attachments: list = None):
    """
    Sends an email

    Parameters
    ----------
    to_address : str
        The email address corresponding to the desired recipient

    subject : str
        The title of the email

    body_text : str
        The text contained within the email

    attachments : list
        A list containing file names of attachments to be sent

    Returns
    -------
    bool
        Whether the email was successfully sent
    """
    st = timeit.default_timer()
    try:
        # Use oauth2 .JSON file and associated company email to connect to the client
        yag = yagmail.SMTP("turtletennisgear@gmail.com", oauth2_file="oauth2-credits.json")
        email_body = f"{body_text}\n\nFrom the Turtle Tennis team."
        yag.send(to=to_address,
                 subject=subject,
                 contents=email_body,
                 attachments=attachments)
        print(timeit.default_timer() - st)
        return True
    # If no internet connection
    except TimeoutError and socket.gaierror:
        print(timeit.default_timer() - st)
        return False


def sort_products_by(products: list,
                     field_name: str,
                     is_desc: bool = False):
    """
    Sort a set of products by a field

    Parameters
    ----------
    products : list
        A list of dictionaries which hold information about the original product set.
        Keys should state the field names.
        Values should state the corresponding field values

    field_name : str
        The name of the field to sort by

    is_desc : bool
        A value used to indicate whether the set should be sorted in descending order or not.
        The value will be True if it should be sorted in descending order and False if it should be ascending

    Returns
    -------
    list
        A list of dictionaries of sorted products
    """
    return sorted(products, key=lambda product: product[field_name], reverse=is_desc)


def create_best_selling_report(days_back: int):
    """
    Creates a report of a the bestselling products over a past number of days

    Parameters
    ----------
    days_back : int
        The number of past days the data should be from

    Returns
    -------
    str
        The file name for the report pdf created
    """
    pdf = FPDF()
    pdf.add_page()
    header_h = create_report_header(pdf, title="Best selling products")

    # Calculate timeframe
    end_of_timeframe = datetime.today()
    start_of_timeframe = datetime.today() - timedelta(days=days_back)
    timeframe = f"{start_of_timeframe.strftime('%d/%m/%y')} - {end_of_timeframe.strftime('%d/%m/%y')}"

    pdf.set_xy(10, header_h + 20)
    pdf.set_font("Poppins-Regular", size=16)
    pdf.set_text_color(r=128, g=128, b=128)
    pdf.cell(w=40, txt="By units sold")
    pdf.set_xy(-80, header_h + 15)
    pdf.cell(w=70, txt="Data collected from", align="R")
    pdf.ln()
    pdf.set_x(-50)
    pdf.add_font(fname="Inter-Regular.ttf")
    pdf.set_font("Inter-Regular", size=20)
    pdf.set_text_color(r=0, g=0, b=0)
    pdf.cell(w=40, txt=f"{timeframe}", align="R")

    all_products = crud.search_table("ecommerce",
                                     "Product",
                                     ["*"],
                                     "")
    dataset = []
    for product in all_products:
        # Create dataset per product
        product_dataset = {}
        product_id = product.get("product_id")
        # Add name, units sold, profit generated to the dataset
        product_dataset["name"] = product.get("name")
        product_dataset["units_sold"] = get_total_sold(product_id, days_back)
        # Profit generated = (total sold * price) - (total sold * cost)
        total_sold = get_total_sold(product_id, days_back)
        product_dataset["profit_generated"] = (total_sold * product.get("sale_price") - (total_sold * product.get("order_cost")))
        # Add the product dataset to the overall one
        dataset.append(product_dataset)

    # If less than the maximum of 5 products exist
    if len(all_products) < 5:
        ending_index = len(all_products) + 1
    else:
        ending_index = 6
    top_five_products_by_units = sort_products_by(dataset, field_name="units_sold", is_desc=True)[0:ending_index]
    top_five_products_by_profit = sort_products_by(dataset, field_name="profit_generated", is_desc=True)[0:ending_index]

    current_date_and_time = datetime.now().strftime("%d-%m-%y_%H-%M-%S")
    # Plot units sold graph
    pdf.ln(20)
    pdf.set_x(10 + pdf.epw/4)
    # Create object of plt class to enable threading to work
    units_sold_labels = [product.get("name") for product in top_five_products_by_units]
    units_sold_values = [product.get("units_sold") for product in top_five_products_by_units]
    fig = Figure()
    fig.set_size_inches(12, 4.8)
    ax = Subplot(fig, 111)
    ax.axis["top"].set_visible(False)
    ax.axis["right"].set_visible(False)
    fig.add_subplot(ax)
    # Save plot as a file, then enter the plot into the pdf by creating an image of that file
    ax.bar(units_sold_labels, units_sold_values, color=colours.get_primary_colour())
    ax.set_xlabel("Product name")
    ax.set_ylabel("Units sold")
    units_sold_chart_file = f"{get_report_directory('plotted_figures')}units_sold_chart_{current_date_and_time}.png"
    fig.savefig(units_sold_chart_file, bbox_inches="tight")
    pdf.image(units_sold_chart_file, w=pdf.epw / 2, h=60)

    pdf.ln(20)
    pdf.set_x(10)
    pdf.set_font("Poppins-Regular", size=16)
    pdf.set_text_color(r=128, g=128, b=128)
    pdf.cell(w=40, txt="By profit generated")
    # Plot profits generated graph
    pdf.ln(20)
    pdf.set_x(10 + pdf.epw / 4)
    # Clear plot for new figure
    profit_generated_labels = [product.get("name") for product in top_five_products_by_profit]
    profit_generated_values = [product.get("profit_generated") for product in top_five_products_by_profit]
    # Create object of plt class to enable threading to work
    fig = Figure()
    fig.set_size_inches(12, 4.8)
    ax = Subplot(fig, 111)
    ax.axis["top"].set_visible(False)
    ax.axis["right"].set_visible(False)
    fig.add_subplot(ax)
    # Save plot as a file, then enter the plot into the pdf by creating an image of that file
    ax.bar(profit_generated_labels, profit_generated_values, color=colours.get_primary_colour())
    ax.set_xlabel("Product name")
    ax.set_ylabel("Profit generated (£)")
    profit_generated_chart_file = f"{get_report_directory('plotted_figures')}profit_generated_chart_{current_date_and_time}.png"
    fig.savefig(profit_generated_chart_file, bbox_inches="tight")
    pdf.image(profit_generated_chart_file, w=pdf.epw/2, h=60)

    # Create pdf document and save to application folder
    file_name = f"{get_report_directory('best_selling_products')}best_selling_products_{current_date_and_time}.pdf"
    pdf.output(name=file_name)

    return file_name


def try_login(username: str,
              password: str):
    """
    Determines whether credentials entered by a user are valid for an existing account

    Parameters
    ----------
    username : str
        The username that the user entered

    password : str
        The password that the user entered

    Returns
    -------
    list
        A list containing fields from an account record that matches the credentials entered.
        The system will return an empty list if no such account could be found
    """
    account_matched = crud.search_table("ecommerce",
                                        "Customer",
                                        ["*"],
                                        f"username = '{encrypt('username', username)}' AND password = '{encrypt('password', password)}'")
    if account_matched:
        return ["Customer", account_matched[0]]
    else:
        account_matched = crud.search_table("ecommerce",
                                            "Staff",
                                            ["*"],
                                            f"username = '{encrypt('username', username)}' AND password = '{encrypt('password', password)}'")
        if account_matched:
            return ["Staff", account_matched[0]]
        else:
            return [None, None]


def validate_customer(field_name: str, field_value: str):
    """
    Validates the fields used to create a customer record

    Parameters
    ----------

    Returns
    -------
    list
        A list containing a boolean element that determines whether the input was valid
        and another element to return any error messages
    """
    error_message = None

    # Username validation
    if field_name == "username":
        username = field_value
        if not validation.presence_check(username):
            error_message = "Must not be blank"
        elif not validation.string_check_alphanumeric(username, False):
            error_message = "Must only contain letters or digits"
        elif not validation.length_check(username, 8, 20):
            error_message = "Must be 8-20 characters"
        elif not validation.uniqueness_check(username, "ecommerce", "Customer", "username") or not validation.uniqueness_check(username, "ecommerce", "Customer", "username"):
            error_message = "Username already taken"
        
    # Password validation
    if field_name == "password":
        password = field_value
        if not validation.presence_check(password):
            error_message = "Must not be blank"
        elif not validation.length_check(password, 8, 20):
            error_message = "Must be 8-20 characters"
        elif not validation.password_check(password):
            error_message = "Must contain uppercase and lowercase letters, digits and no special characters"

    # Name validation
    if field_name == "name":
        name = field_value
        if not validation.presence_check(name):
            error_message = "Must not be blank"
        elif not validation.string_check_alpha(name, False):
            error_message = "Must only contain letters"
        elif not validation.length_check(name, 2, 20):
            error_message = "Must be 2-20 characters"
        
    # Surname validation
    if field_name == "surname":
        surname = field_value
        if not validation.presence_check(surname):
            error_message = "Must not be blank"
        elif not validation.string_check_alpha(surname, False):
            error_message = "Must only contain letters"
        elif not validation.length_check(surname, 2, 20):
            error_message = "Must be 2-20 characters"

    # Email validation
    if field_name == "email_address":
        email_address = field_value
        if not validation.presence_check(email_address):
            error_message = "Must not be blank"
        elif not validation.email_format_check(email_address):
            error_message = "Must be in the form 'example@gmail.com'"

    if error_message is None:
        # Return that the account was created and that there were no error messages
        return [True, None]
    else:
        # Return that the account was not created and the corresponding error message
        return [False, error_message]


def validate_order(field_name: str, field_value: str):
    """
    Validates the fields used to create an order record

    Parameters
    ----------


    Returns
    -------
    list
        A list containing a boolean element that determines whether the input was valid
        and another element to return any error messages
    """
    error_message = None

    # For each field, check whether the field should not be excluded from validation and whether all previous fields
    # are valid

    # Address validation
    if field_name == "delivery_address":
        address = field_value
        if not validation.presence_check(address):
            error_message = "Must not be blank"
        elif not validation.string_check_alphanumeric(address, True):
            error_message = "Must only contain letters or digits"
        elif not validation.length_check(address, 8, 50):
            error_message = "Must be 8-20 characters"

    # Postcode validation
    if field_name == "delivery_postcode":
        postcode = field_value
        if not validation.presence_check(postcode):
            error_message = "Must not be blank"
        elif not validation.postcode_check(postcode):
            error_message = "e.g. BT56 7YD"

    # Delivery cost validation
    if field_name == "delivery_cost":
        del_cost = field_value
        if not validation.presence_check(del_cost):
            error_message = "Must not be blank"
        elif not validation.money_check(del_cost):
            error_message = "Must not contain letters and must be to two decimal places"
        elif not validation.range_check(del_cost, 1, 50):
            error_message = "Must be between 1-50"

    if error_message is None:
        return [True, error_message]
    else:
        return [False, error_message]


def validate_staff(field_name: str, field_value: str):
    """
    Validates the fields used to create a staff record

    Parameters
    ----------


    Returns
    -------
    list
        A list containing a boolean element that determines whether the input was valid
        and another element to return any error messages
    """
    error_message = None

    # For each field, check whether the field should not be excluded from validation and whether all previous fields
    # are valid
    if field_name == "username":
        username = field_value
        if not validation.presence_check(username):
            error_message = "Must not be blank"
        elif not validation.string_check_alphanumeric(username, False):
            error_message = "Must only contain letters or digits"
        elif not validation.length_check(username, 8, 20):
            error_message = "Must be 8-20 characters"
        elif not validation.uniqueness_check(username, "ecommerce", "Staff", "username"):
            error_message = "Username is already taken"

    if field_name == "password":
        password = field_value
        if not validation.presence_check(password):
            error_message = "Must not be left blank"
        elif not validation.password_check(password):
            error_message = "Must contain uppercase and lowercase letters, digits and no special characters"

    if field_name == "name":
        name = field_value
        if not validation.presence_check(name):
            error_message = "Must not be blank"
        elif not validation.string_check_alpha(name, False):
            error_message = "Must only contain letters"
        elif not validation.length_check(name, 2, 20):
            error_message = "Must be 2-20 characters"

    if field_name == "surname":
        surname = field_value
        if not validation.presence_check(surname):
            error_message = "Must not be blank"
        elif not validation.string_check_alpha(surname, False):
            error_message = "Must only contain letters"
        elif not validation.length_check(surname, 2, 20):
            error_message = "Must be 2-20 characters"

    if field_name == "address":
        address = field_value
        if not validation.presence_check(address):
            error_message = "Must not be blank"
        elif not validation.string_check_alphanumeric(address, True):
            error_message = "Must only contain letters or digits"
        elif not validation.length_check(address, 8, 50):
            error_message = "Must be 8-20 characters"

    if field_name == "postcode":
        postcode = field_value
        if not validation.presence_check(postcode):
            error_message = "Must not be blank"
        elif not validation.postcode_check(postcode):
            error_message = "e.g. BT56 7YD"

    if field_name == "weekly_hours":
        total_hours = field_value
        if not validation.presence_check(total_hours):
            error_message = "Must not be blank"
        elif not validation.integer_check(total_hours):
            error_message = "Must be an integer"
        elif not validation.range_check(total_hours, 1, 50):
            error_message = "Must be between 1-50"

    if field_name == "email_address":
        email = field_value
        if not validation.presence_check(email):
            error_message = "Must not be left blank"
        elif not validation.email_format_check(email):
            error_message = "Must be in the form 'example@gmail.com'"
            
    if error_message is None:
        return [True, error_message]
    else:
        return [False, error_message]


def validate_product(field_name: str, field_value: str):
    """
    Validates the fields used to create a product record

    Parameters
    ----------


    Returns
    -------
    list
        A list containing a boolean element that determines whether the input was valid
        and another element to return any error messages
    """
    error_message = None

    # For each field, check whether the field should not be excluded from validation and whether all previous fields
    # are valid
    if field_name == "name":
        name = field_value
        if not validation.presence_check(name):
            error_message = "Must not be blank"
        elif not validation.string_check_alphanumeric(name, True):
            error_message = "Must only contain letters or numbers"
        elif not validation.length_check(name, 2, 20):
            error_message = "Must be 2-20 characters"

    if field_name == "description":
        description = field_value
        if not validation.presence_check(description):
            error_message = "Must not be blank"
        elif not validation.length_check(description, 8, 300):
            error_message = "Must be 8-300 characters"

    if field_name == "current_stock":
        stock = field_value
        if not validation.presence_check(stock):
            error_message = "Must not be blank"
        elif not validation.integer_check(stock):
            error_message = "Must be an integer"
        elif not validation.range_check(stock, 0, 999):
            error_message = "Must be between 0-999"

    if field_name == "order_cost":
        order_cost = field_value
        if not validation.presence_check(order_cost):
            error_message = "Must not be blank"
        elif not validation.money_check(order_cost):
            error_message = "Must not contain letters and must be to two decimal places"
        elif not validation.range_check(order_cost, 1, 999):
            error_message = "Must be between 1- 999"

    if field_name == "sale_price":
        sale_price = field_value
        if not validation.presence_check(sale_price):
            error_message = "Must not be blank"
        elif not validation.money_check(sale_price):
            error_message = "Must not contain letters and must be to two decimal places"
        elif not validation.range_check(sale_price, 1, 999):
            error_message = "Must be between 1-999"

    if error_message is None:
        return [True, error_message]
    else:
        return [False, error_message]


def validate_payment_card(field_name: str, field_value: str):
    """
    Validates the fields used to create a payment card record

    Parameters
    ----------


    Returns
    -------
    list
        A list containing a boolean element that determines whether the input was valid
        and another element to return any error messages
    """
    error_message = None

    if field_name == "card_number":
        card_num = field_value
        if not validation.card_num_check(card_num):
            error_message = "e.g. XXXX XXXX XXXX XXXX"
        elif not validation.uniqueness_check(card_num, "ecommerce", "Payment_Card", "card_number"):
            error_message = "Card number already taken"

    if field_name == "expiry_date":
        expiry_date = field_value
        if not validation.presence_check(expiry_date):
            error_message = "Must not be blank"
        elif not validation.expiry_date_check(expiry_date):
            error_message = "e.g. 07/27"

    if field_name == "cvc":
        cvc = field_value
        if not validation.presence_check(cvc):
            error_message = "Must not be blank"
        elif not validation.string_check_numeric(cvc, False) or not validation.length_check(cvc, 3, 3):
            error_message = "e.g. 345"

    if field_name == "cardholder_name":
        holder_name = field_value
        if not validation.presence_check(holder_name):
            error_message = "Must not be blank"
        elif not validation.string_check_alpha(holder_name, True):
            error_message = "Must only contain letters"
        elif not validation.length_check(holder_name, 2, 50):
            error_message = "Must be 2-50 characters"

    if field_name == "billing_address":
        billing_address = field_value
        if not validation.presence_check(billing_address):
            error_message = "Must not be blank"
        elif not validation.string_check_alphanumeric(billing_address, True):
            error_message = "Must only contain letters or digits"
        elif not validation.length_check(billing_address, 8, 50):
            error_message = "Must be 8-50 characters"

    if field_name == "billing_postcode":
        billing_postcode = field_value
        if not validation.presence_check(billing_postcode):
            error_message = "Must not be blank"
        elif not validation.postcode_check(billing_postcode):
            error_message = "e.g. BT56 7YD"

    if error_message is None:
        return [True, error_message]
    else:
        return [False, error_message]


def validate_supplier(field_name: str, field_value: str):
    """
    Validates the fields used to create a payment card record

    Parameters
    ----------

    Returns
    -------
    list
        A list containing a boolean element that determines whether the input was valid
        and another element to return any error messages
    """
    error_message = None

    if field_name == "company_name":
        company_name = field_value
        if not validation.presence_check(company_name):
            error_message = "Must not be blank"
        elif not validation.string_check_alphanumeric(company_name, spaces_allowed=True):
            error_message = "Must only contain letters, numbers or spaces"
        elif not validation.length_check(company_name, 4, 50):
            error_message = "Must be 4-50 characters long!"

    if field_name == "telephone_num":
        if not validation.phone_number_check(field_value):
            error_message = "e.g. 07656463212"

    if error_message is None:
        return [True, error_message]
    else:
        return [False, error_message]
