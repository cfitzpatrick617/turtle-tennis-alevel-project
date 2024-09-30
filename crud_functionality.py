import os
import sqlite3

import backend


def create_recovery_database():
    """
    Contingency procedure to create a blank database with an admin account if
    the database has i) been deleted and ii) cannot be recovered via a backup
    """
    # Customer table
    create_table("ecommerce",
                 "Customer",
                 """customer_id INTEGER PRIMARY KEY,
                 username char(20) NOT NULL,
                 password char(20) NOT NULL,
                 name char(20) NOT NULL,
                 surname char(20) NOT NULL,
                 email_address char(74) NOT NULL""",
                 None)

    # Create staff table and add admin account
    create_table("ecommerce",
                 "Staff",
                 """staff_id INTEGER PRIMARY KEY,
                 username char(20) NOT NULL,
                 password char(20) NOT NULL,
                 name char(20) NOT NULL,
                 surname char(20) NOT NULL,
                 address char(50) NOT NULL,
                 postcode char(8) NOT NULL,
                 weekly_hours INTEGER NOT NULL,
                 email_address char(74) NOT NULL,
                 access_level char(10) NOT NULL""",
                 None)

    add_record("ecommerce",
               "Staff",
               {"username": "management",
                "password": "Tt123",
                "name": "Calum",
                "surname": "Fitzpatrick",
                "address": "30 Egg Fields",
                "postcode": "BT65 7YD",
                "weekly_hours": "30",
                "email_address": "turtletennisgear@gmail.com",
                "access_level": "Management"})

    # Payment card table
    create_table("ecommerce",
                 "Payment_Card",
                 """payment_card_id INTEGER PRIMARY KEY,
                 card_number char(19) NOT NULL,
                 cvc char(3) NOT NULL,
                 expiry_date char(5) NOT NULL,
                 cardholder_name char(20) NOT NULL,
                 billing_address char(50) NOT NULL,
                 billing_postcode char(8) NOT NULL,
                 customer_id INTEGER NOT NULL""",
                 {"customer_id": "Customer(customer_id)"})

    # Orders table
    create_table("ecommerce",
                 "Orders",
                 """order_id INTEGER PRIMARY KEY,
                 date char(10) NOT NULL,
                 delivery_address char(50) NOT NULL,
                 delivery_postcode char(50) NOT NULL,
                 delivery_cost REAL NOT NULL,
                 total_cost REAL NOT NULL,
                 delivery_status char(15) NOT NULL,
                 customer_id INTEGER NOT NULL,
                 payment_card_id INTEGER NOT NULL""",
                 {"customer_id": "Customer(customer_id)",
                  "payment_card_id": "Payment_Card(payment_card_id)"})

    # Supplier table
    create_table("ecommerce",
                 "Supplier",
                 """supplier_id INTEGER PRIMARY KEY,
                 company_name char(20) NOT NULL,
                 telephone_num char(11) NOT NULL""",
                 None)

    # Product table
    create_table("ecommerce",
                 "Product",
                 """product_id INTEGER PRIMARY KEY,
                 name CHAR(20) NOT NULL,
                 description TEXT NOT NULL,
                 category TEXT NOT NULL,
                 current_stock INTEGER NOT NULL,
                 average_rating REAL NOT NULL,
                 order_cost REAL NOT NULL,
                 sale_price REAL NOT NULL,
                 total_sold INTEGER NOT NULL,
                 image_file TEXT NOT NULL,
                 supplier_id INTEGER NOT NULL""",
                 {"supplier_id": "Supplier(supplier_id)"})

    # Linking table between order and product
    create_table("ecommerce",
                 "Order_Product",
                 """order_product_id INTEGER PRIMARY KEY,
                 quantity INTEGER NOT NULL,
                 order_id INTEGER NOT NULL,
                 product_id INTEGER NOT NULL""",
                 {"order_id": "Orders(order_id)",
                  "product_id": "Product(product_id)"})

    # Ratings table
    create_table("ecommerce",
                 "Ratings",
                 """rating_id INTEGER PRIMARY KEY,
                 score INTEGER NOT NULL,
                 date char(10) NOT NULL,
                 customer_id INTEGER NOT NULL,
                 product_id INTEGER NOT NULL""",
                 {"customer_id": "Customer(customer_id)",
                  "product_id": "Product(product_id)"})


def recover_database(database_name: str):
    """
    Attempts to recover the database to the most recent backup

    Parameters
    ----------
    database_name : str
        The name of the database
    """
    if not os.path.exists(f"{database_name}.db"):
        backup_directory = backend.get_directory("backups")
        # Count number of files in directory
        # Source: https://stackoverflow.com/questions/2632205/how-to-count-the-number-of-files-in-a-directory-using-python
        file_count = sum(len(files) for _, _, files in os.walk(backup_directory))
        # If no backups, create a blank database with admin account instead
        if file_count == 0:
            with open(f"{database_name}.db", "x") as _:
                pass
            create_recovery_database()
        else:
            backup_file_name, _ = backend.get_recent_backup(database_name)
            # Copy backup into new database file
            os.system(f"copy backups\\{backup_file_name} {database_name}.db")


def open_database(database_name: str):
    """
    Function used to open and connect to a SQLite3 database.

    Parameters
    ------------
    database_name : str
        The name of the database to connect to.

    Returns
    ------------
    sqlite3.Connection
        A connection object that allows the program to interact with the SQLite3
        database found in the "database_name.db" file.


    sqlite3.Cursor
        A cursor object that allows the program to execute provided SQL statements
        on the database found in the "database_name.db" file.
    """
    # Recover database if it cannot be found
    if not os.path.exists(f"{database_name}.db"):
        recover_database(database_name)
    conn = sqlite3.connect(f"{database_name}.db")
    # Enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()
    return [conn, cur]


def create_table(database_name: str,
                 table_name: str,
                 fields_string: str,
                 fk_and_ref_dict: dict):
    """
    Function used to create a new table in the chosen database, including setting up fields,
    field types, foreign key references and data integrity restrictions.

    Parameters
    ------------
    database_name : str
        The name of the database to add the table to.

    table_name : str
        The name of the table that will be created

    fields_string : str
        The field names and data types for all fields excluding foreign keys.
        Fields should be separated by a command and a primary key should be identified.

    fk_and_ref_dict : dict
        A dictionary of all foreign keys and references.
        Keys should state the foreign key name.
        Values should state the associated foreign key's reference.
    """
    conn, cur = open_database(database_name)

    # Convert the list of fields into the correct format and add to the command
    create_command = f"CREATE TABLE IF NOT EXISTS {table_name}(" + f"{fields_string}"

    if fk_and_ref_dict is not None:
        # Convert the dictionary of foreign key / references into the correct format and add to the command
        for key, value in fk_and_ref_dict.items():
            # Set the reference and the protocols for updating and deleting fields
            create_command += f", FOREIGN KEY({key}) REFERENCES {value} ON UPDATE CASCADE ON DELETE CASCADE"

    print(create_command)
    cur.execute(f"{create_command});")
    conn.commit()
    conn.close()


def add_record(database_name: str,
               table_name: str,
               non_pk_values: dict):
    """
    Function used to add a new record to a table in the chosen database.

    Parameters
    ------------
    database_name : str
        The name of the database that holds the correct table.

    table_name : str
        The name of the table to add the record to.

    non_pk_values : dict
        The values of all non primary-key fields in the record to be added.
    """
    conn, cur = open_database(database_name)

    field_names = get_table_headings(database_name, table_name)[1:]
    values_in_order = []
    for field in field_names:
        # Enforce encryption
        decrypted_field = str(non_pk_values[field])
        encrypted_field = backend.encrypt(field, decrypted_field)
        values_in_order.append(encrypted_field)

    # Conjoin the non-primary key values with a comma between each value
    values = "', '".join(values_in_order)
    # Note: ID is not included as SQL will auto-increment it
    cur.execute(f"INSERT INTO {table_name} VALUES (NULL, '{values}');")
    conn.commit()
    conn.close()


def search_table(database_name: str,
                 table_name: str,
                 scope_of_record: list,
                 search_parameters: str):
    """
    Function used to search and return specific fields from records that match predefined criteria.

    Parameters
    ------------
    database_name : str
        The name of the database that holds the correct table.

    table_name : str
        The name of the table to search in.

    scope_of_record : list
        The fields that should be returned from records that match the search criteria. All
        elements will be of type str.

    search_parameters : dict
        The SQL conditions that specify which records should be returned.
        Must be in the form "fieldName = 'value' OPERATOR ..."
        Null search parameters should be passed as ""

    Returns
    ------------
    list
        A list of tuples containing the required fields from records that match
        the search criteria.
    """
    
    conn, cur = open_database(database_name)
    # Conjoin the scope fields with a comma between each field
    scope = ", ".join(scope_of_record)
    search_command = f"SELECT {scope} FROM {table_name}"

    # If there are search parameters present i.e, the user does not want to return the whole table
    if search_parameters != "":
        search_command += f" WHERE {search_parameters}"

    cur.execute(f"{search_command};")
    # Return required fields from records that match the search criteria
    rows = cur.fetchall()

    # Format results into a dictionary that removes the need for indexes
    if scope_of_record[0] == "*":
        field_names = get_table_headings(database_name, table_name)
    else:
        field_names = scope_of_record
        
    results = []
    for row in rows:
        # Enforce decryption
        results.append({field_names[count]: backend.decrypt(field_names[count], field)
                        for count, field in enumerate(row)})

    return results


def search_joined_table(database_name: str,
                        starting_table: str,
                        table_and_links: list,
                        scope_of_record: list,
                        search_parameters: str):
    """
    Function used to join tables, and then search and return specific fields from records
    that match predefined criteria in said table.

    Parameters
    ------------
    database_name : str
        The name of the database that holds the correct table.

    starting_table : str
        The name of the first table in the chain.

    table_and_links : list
        A two-dimensional list representing a chain of tables that connect in order.
        The list should be written as:
        [ [table_1_name, table_1_id], [table_2_name, table_2_id]... ] where table_1 connects to table_2 and so on.
        
    scope_of_record : list
        The fields that should be returned from records that match the search criteria. All
        elements will be of type str.

    search_parameters : str
        The SQL conditions that specify which records should be returned.
        Must be in the form "fieldName = 'value' OPERATOR ..."
        Null search parameters should be passed as ""

    Returns
    ------------
    list
        A list of tuples containing the required fields from records that match
        the search criteria.
    """
        
    conn, cur = open_database(database_name)
    # Conjoin the scope fields with a comma between each field
    scope = ", ".join(scope_of_record)
    # Set the first table in the join chain to the starting table
    search_command = f"SELECT {scope} FROM {starting_table}"

    previous_table_name = None
    # Iterate through the table chain
    for count, table in enumerate(table_and_links):
        current_table_name = table[0]
        current_table_id = table[1]
        table_to_join = current_table_name
        # If the table is joining to the original table
        if count == 0:
            table_to_join_to = starting_table
        else:
            # The table joins to the previous table in the chain
            table_to_join_to = previous_table_name
        joining_id = current_table_id
        # Set the previous table as the current table
        previous_table_name = current_table_name
        # Add SQL syntax
        search_command += f""" INNER JOIN {table_to_join}
                              ON {table_to_join_to}.{joining_id}
                              = {table_to_join}.{joining_id}"""

    # If there are search parameters present i.e, the user does not want to return the whole table
    if search_parameters != "":
        search_command += f" WHERE {search_parameters}"

    cur.execute(f"{search_command};")
    # Return required fields from records that match the search criteria
    rows = cur.fetchall()

    if scope_of_record[0] == "*":
        field_names = get_table_headings(database_name, starting_table)
        for table_and_link in table_and_links:
            table_name = table_and_link[0]
            field_names += get_table_headings(database_name, table_name)
    else:
        field_names = scope_of_record

    results = []
    for row in rows:
        results.append({field_names[count]: backend.decrypt(field_names[count], field)
                        for count, field in enumerate(row)})

    return results


def update_record(database_name: str,
                  table_name: str,
                  update_data_dict: dict,
                  update_parameters: str,
                  override_encryption_status: bool = False):
    """
    Function used to update a record that matches predefined criteria.

    Parameters
    ------------
    database_name : str
        The name of the database that holds the correct table.

    table_name : str
        The name of the table to update in.

    update_data_dict : dict
        A dictionary of fields and their associated updated values.
        Keys should state the field name.
        Values should state their associated field's new value.

    update_parameters : str
        The SQL conditions that specify which records should be updated. Must be in the form
        "fieldName = 'value' OPERATOR ..."
    """

    conn, cur = open_database(database_name)
    update_command = f"UPDATE {table_name} SET "

    # Convert the dictionary of foreign key / references into the correct format and add to the command
    for key, value in update_data_dict.items():
        update_command += f"{key} = '{backend.encrypt(key, value, override_encryption_status)}',"
    update_command = update_command[:-1] + f" WHERE {update_parameters}"
    print(update_command)

    cur.execute(f"{update_command};")
    conn.commit()
    conn.close()


def delete_record(database_name: str,
                  table_name: str,
                  delete_parameters: str):
    """
    Function used to delete records that match predefined criteria.

    Parameters
    ------------
    database_name : str
        The name of the database that holds the correct table.

    table_name : str
        The name of the table to search in.

    delete_parameters : str
        The SQL conditions that specify which records should be deleted. Must be in the form
        "fieldName = value OPERATOR ..."
    """
    
    conn, cur = open_database(database_name)
    # Delete record where the conditions set are satisfied
    cur.execute(f"DELETE FROM {table_name} WHERE {delete_parameters};")
    conn.commit()
    conn.close()


def get_table_headings(database_name: str,
                       table_name: str):
    """
    Gets the column headings (field names) of a table in a database

    Parameters
    ----------
    database_name : str
        The name of the database which holds the correct table

    table_name : str
        The name of the table whose headings are required

    Returns
    -------
    list
        The column headings in the order they are presented in the table
    """
    conn, cur = open_database(database_name)
    cur.execute(f"SELECT * FROM {table_name}")
    return [description[0] for description in cur.description]


def get_max_length(field_name: str):
    abnormal_lengths = {"email_address": 74,
                        "card_number": 19,
                        "cvc": 3,
                        "expiry_date": 5,
                        "cardholder_name": 50,
                        "billing_address": 50,
                        "billing_postcode": 8,
                        "delivery_address": 50,
                        "delivery_postcode": 8,
                        "company_name": 50,
                        "telephone_num": 11,
                        "address": 50,
                        "postcode": 8,
                        "weekly_hours": 2,
                        "description": 300,
                        "current_stock": 3,
                        "order_cost": 6,
                        "sale_price": 6,
                        "image_file": 50}
    if field_name in abnormal_lengths.keys():
        return abnormal_lengths.get(field_name)
    else:
        return 20
