import datetime


def check_date_validity(text: str) -> bool | str:

    """Function to check for the entered data to match defined format"""

    try:
        datetime.datetime.strptime(text, '%Y-%m-%d')
        return True
    except ValueError:
        return "Please enter the date in correct format (yyyy-mm-dd)."


def check_date_in_future(text: str) -> bool | str:

    """Function that checks for the inputed data for end date in habit parameters not in the past"""

    valid_format = check_date_validity(text)
    if valid_format is not True:
        return valid_format
    try:
        end_date = datetime.date.fromisoformat(text)
        if end_date < datetime.date.today():
            return "Incorrect end date."
        return True 
    except ValueError:
        return "Date format is invalid."