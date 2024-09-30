import datetime
import re
from typing import Union

import crud_functionality as crud


def card_num_check(value_to_check: str):
    """
    Checks whether a card number is in the format 'NNNN NNNN NNNN NNNN'

    Parameters
    ----------
    value_to_check : str
        The input that the validation should be performed on

    Returns
    -------
    bool
        Whether the input is in the correct format for a card number.
        The value will be True if the input was valid and False if not
    """
    if re.fullmatch("[0-9]{4} [0-9]{4} [0-9]{4} [0-9]{4}", value_to_check):
        return True
    else:
        return False


def date_check(value_to_check: str):
    """
    Checks whether an input is in the format YYYY-MM-DD

    Parameters
    ----------
    value_to_check : str
        The input that the validation check should be performed on

    Returns
    -------
    bool
        Whether the input is in the correct format for a date
        The value will be True if the input was valid and False if not
    """
    try:
        datetime.datetime.strptime(value_to_check, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def email_format_check(value_to_check: str):
    """
    Checks whether an input is in the correct email format

    Parameters
    ----------
    value_to_check : str
        The input that the validation check should be performed on

    Returns
    -------
    bool
        Whether the input is in the correct format for an email.
        The value will be True if the input was valid and False if not
    """
    if re.fullmatch("[A-Za-z0-9]{1,64}@gmail.com", value_to_check):
        return True
    else:
        return False


def expiry_date_check(value_to_check: str):
    """
    Checks whether an expiry date is in the correct format

    Parameters
    ----------
    value_to_check : str
        The input that the validation check should be performed on

    Returns
    -------
    bool
        Whether the input is in the correct format for an expiry date.
        The value will be True if the input was valid and False if not
    """
    if re.fullmatch("[0-9]{2}/[0-9]{2}", value_to_check):
        return True
    else:
        return False


def fk_constraint_check(value_to_check: object,
                        search_table_name: str,
                        fk_field: str):
    """
    Checks whether a foreign key ID corresponds with an existing record
    in the appropriate table in which it links to

    Parameters
    ----------
    value_to_check : object
        The input that the validation check should be performed on

    search_table_name : str
        The name of the table on which the validation check should be performed on

    fk_field : str
        The name of the foreign key field

    Returns
    -------
    bool
        Whether the foreign key ID corresponds with an existing record in the required table.
        The value will be True if the input was valid and False if not
    """
    if crud.search_table("ecommerce",
                         search_table_name,
                         ["*"],
                         f"{fk_field} = '{value_to_check}'"):
        return True
    else:
        return False


def integer_check(value_to_check: object):
    """
    Checks whether an input is an integer

    Parameters
    ----------
    value_to_check : object
        The input that the validation check should be performed on

    Returns
    -------
    bool
        Whether the input was an integer.
        The value will be True if the input was valid and False if not
    """
    try:
        int(value_to_check)
        return True
    except ValueError:
        return False


def length_check(value_to_check: str,
                 minimum: int,
                 maximum: int):
    """
    Checks whether a string input conforms to
    a pre-specified minimum and maximum length.
    
    Parameters
    ------------
    value_to_check : str
        The input that the validation check should be performed on

    minimum : int
        The minimum length that the string input should be

    maximum: int
        The maximum length that the string input should be

    Returns
    -------
    bool
        Whether the input was between the minimum and maximum length specified.
        The value will be True if the input was valid and False if not
    """
    if minimum <= len(value_to_check) <= maximum:
        return True
    else:
        return False


def lookup_check(value_to_check: object,
                 validation_list: list):
    """
    Checks whether an input is in a pre-specified list of values

    Parameters
    ----------
    value_to_check : object
        The input that the validation check should be performed on

    validation_list : list
        The list of values that the input will be checked against

    Returns
    -------
    bool
        Whether the input was in the list of values.
        The value will be True if the input was valid and False if not
    """
    if value_to_check in validation_list:
        return True
    else:
        return False


def money_check(value_to_check: object):
    """
    Checks whether an input is in the de-facto format for money

    Parameters
    ----------
    value_to_check : object
        The input that the validation check should be performed on

    Returns
    -------
    bool
        Whether the input was in the correct format for money.
        The value will be True if the input was valid and False if not
    """
    if not real_check(value_to_check):
        return False
    else:
        formatted_value = "{:.2f}".format(float(value_to_check))
        if float(formatted_value) - float(value_to_check) != 0:
            return False
        else:
            return True


def password_check(value_to_check: str):
    """
    Checks whether a string input conforms to the system's rules for passwords

    Parameters
    ----------
    value_to_check : str
        The input that the validation check should be performed on

    Returns
    -------
    bool
        Whether the input was in the correct format for a password.
        The value will be True if the input was valid and False if not
    """
    if (
        # If the input is an alphanumeric string...
        string_check_alphanumeric(value_to_check, False) is True
        # that contains at least one digit...
        and any(char.isdigit() for char in value_to_check)
        # and does not consist only of upper case letters...
        and value_to_check.isupper() is False
        # and does not consist only of lower case letter then...
        and value_to_check.islower() is False
       ):
        return True
    else:
        return False


def string_check_alpha(value_to_check: str,
                       spaces_allowed: bool):
    """
    Checks whether a string input consists of only alphabetical characters

    Parameters
    ----------
    value_to_check : str
        The input that the validation check should be performed on

    spaces_allowed : bool
        A value used to indicate whether space characters are valid.
        The value will be True if spaces are permitted and False if not

    Returns
    -------
    bool
        Whether the input is an alphabetical string only.
        The value will be True if the input was valid and False if not
    """
    # If all characters have ASCII values corresponding to capital letters
    # NOTE: .upper() is used as the case is not important
    if not spaces_allowed:
        if all(65 <= ord(char) <= 90 for char in value_to_check.upper()):
            return True
        # If any characters are non-alphabetical
        else:
            return False
    else:
        # If all characters have ASCII values corresponding to capital letters or are spaces
        if all(65 <= ord(char) <= 90
               or char == " "
               for char in value_to_check.upper()
               ):
            return True
        else:
            return False


def string_check_numeric(value_to_check: str,
                         spaces_allowed: bool):
    """
    Checks whether a string input only consists of numeric characters

    Parameters
    ----------
    value_to_check : str
        The input that the validation check should be performed on

    spaces_allowed : bool
        A value used to indicate whether space characters are valid.
        The value will be True if spaces are permitted and False if not

    Returns
    -------
    bool
        Whether the input was a numeric string only.
        The value will be True if the input was valid and False if not
    """
    # If all characters have ASCII values corresponding to numbers
    if not spaces_allowed:
        if all(48 <= ord(char) <= 57 for char in value_to_check):
            return True
        # If any characters are non-alphabetical
        else:
            return False
    else:
        # If all characters have ASCII values corresponding to capital letters or are spaces
        if all(48 <= ord(char) <= 57
               or char == " "
               for char in value_to_check
               ):
            return True
        else:
            return False


def string_check_alphanumeric(value_to_check: str,
                              spaces_allowed: bool):
    """
    Checks whether a string input only consists of alphanumeric characters

    Parameters
    ----------
    value_to_check : str
        The input that the validation check should be performed on

    spaces_allowed : bool
        A value used to indicate whether space characters are valid.
        The value will be True if spaces are permitted and False if not

    Returns
    -------
    bool
        Whether the input was an alphanumeric string only.
        The value will be True if the input was valid and False if not
    """
    if all(
           # If all characters have either ASCII values corresponding to capital letters...
           string_check_alpha(char, spaces_allowed) is True
           # OR have ASCII values corresponding to digits...
           or string_check_numeric(char, spaces_allowed) is True
           for char in value_to_check
           ):
        return True
    else:
        # If any characters is neither a letter or digit (or space)
        return False


def real_check(value_to_check: object):
    """
    Checks whether an input is a real number

    Parameters
    ----------
    value_to_check : object
        The input that the validation check should be performed on

    Returns
    -------
    bool
        A value used to indicate whether the input is valid.
        The value will be True if the input was valid and False if not
    """
    try:
        float(value_to_check)
        return True
    except ValueError:
        return False


def range_check(value_to_check: Union[int, float],
                minimum: int,
                maximum: int):
    """
    Checks whether a numerical input is between a pre-specified range

    Parameters
    ----------
    value_to_check : int | float
        The input that the validation check should be performed on

    minimum : int | float
        The minimum value that the input should be

    maximum: int | float
        The maximum value that the input should be

    Returns
    -------
    bool
        A value used to indicate whether the input is valid.
        The value will be True if the input was valid and False if not
    """
    if minimum <= float(value_to_check) <= maximum:
        return True
    else:
        return False


def presence_check(value_to_check):
    """
    Checks whether an input is not empty

    Parameters
    ----------
    value_to_check
        The input that the validation check should be performed on

    Returns
    -------
    bool
        A value used to indicate whether the input is null.
        The value will be True if the input was not null and False if not
    """
    if value_to_check is not None and value_to_check != "":
        return True
    else:
        return False


def postcode_check(value_to_check: str):
    """
    Checks whether a string input matches the de-facto format for postcodes

    Parameters
    ----------
    value_to_check : str
        The input that the validation check should be performed on

    Returns
    -------
    bool
        A value used to indicate whether the input is valid.
        The value will be True if the input was valid and False if not
    """
    if re.fullmatch("[A-Z]{2}[0-9]{2} [0-9][A-Z]{2}", value_to_check.upper()):
        return True
    else:
        return False


def phone_number_check(value_to_check: str):
    """
    Checks whether a string value is in the de-facto format for a phone number

    Parameters
    ----------
    value_to_check : str
        The input that the validation check should be performed on

    Returns
    -------
    bool
        Whether the input is in the correct format for a phone number.
        The value will be True if the input was valid and False if not
    """
    if value_to_check.isnumeric() and length_check(value_to_check, 11, 11):
        return True
    else:
        return False


def uniqueness_check(value_to_check: object,
                     database_to_check: str,
                     table_to_check: str,
                     field_to_check: str):
    """
    Checks whether a field value is unique (i.e. does not already exist)
    in a specified database table

    Parameters
    ----------
    value_to_check : object
        The input that the validation check should be performed on

    database_to_check : str
        The name of the database which contains the appropriate table to check

    table_to_check : str
        The name of the table on which the input should be matched against

    field_to_check : str
        The name of the field which is being checked for

    Returns
    -------
    bool
        A value used to indicate whether the input is valid.
        The value will be True if the input was valid and False if not
    """
    # Get a list of records within the table that contain the same value for the corresponding field
    search_returns = crud.search_table(database_to_check,
                                       table_to_check,
                                       [f"{field_to_check}"],
                                       f"{field_to_check} = '{value_to_check}'")
    # If the list returned is empty
    if not search_returns:
        return True
    else:
        return False
