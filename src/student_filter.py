import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Tuple

def filter_incoming_student(row: pd.Series, current_date: Optional[datetime] = None) -> str | None:
    """
    Filters incoming students based on their arrival date and accessibility requirements.

    Args:
        row (pd.Series): A row of the incoming students DataFrame.
        current_date (Optional[datetime]): The current date to compare with. Defaults to None, in which case the current date is used.

    Returns:
        str | None: A string indicating the reason for filtering out the student, or None if the student passes the filter.
    """
    date_arriving = pd.to_datetime(row['Arrival'], format='%d/%m/%Y')

    three_months_from_now = (current_date or datetime.now()) + timedelta(days=90)

    if date_arriving < datetime.now():
        row.loc['Arrival'] = datetime.today()
        date_arriving = datetime.today()

    if not date_arriving <= three_months_from_now:
        return 'Arriving too late'

    try:
        disability_status = row[
            'Do you have any accessibility requirements you would like us to be aware of or need any sort of support?']

        if disability_status == 'Yes (please fill in below)':
            return 'Incoming student disability'
    except KeyError:
        pass

    return None



def filter_local_student(row: pd.Series, current_date: Optional[datetime] = None) -> str | None:
    """
    Filters local students based on their availability date.

    Args:
        row (pd.Series): A row of the local students DataFrame.
        current_date (Optional[datetime]): The current date to compare with. Defaults to None, in which case the current date is used.

    Returns:
        str | None: A string indicating the reason for filtering out the student, or None if the student passes the filter.
    """

    date_available = pd.to_datetime(
        row['Availability'],
        format='%d/%m/%Y')

    three_months_from_now = (current_date or datetime.now()) + timedelta(days=90)

    if date_available is pd.NaT:
        return 'Date not entered correctly - reformat and read to input'

    if date_available < datetime.now():
        row.loc[
            'Availability'] = datetime.today()
        date_available = datetime.today()

    if not date_available <= three_months_from_now:
        return 'Available too late'

    return None



def apply_filters(local_students: pd.DataFrame, incoming_students: pd.DataFrame, current_date: Optional[datetime] = None) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Applies filters to both local and incoming students DataFrames to separate out students based on certain criteria.

    This function performs the following operations:
    1. Applies the filter_local_student function to each row of the local_students DataFrame.
    2. Applies the filter_incoming_student function to each row of the incoming_students DataFrame.
    3. Separates out the rows that do not meet the criteria (filtered out) into separate DataFrames.
    4. Drops the 'reason' column used for filtering from the remaining DataFrames.

    Args:
        local_students (pd.DataFrame): DataFrame containing local students' data.
        incoming_students (pd.DataFrame): DataFrame containing incoming students' data.
        current_date (Optional[datetime]): The current date to use for filtering. Defaults to None, in which case the current date is used.

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        - Cleaned local students DataFrame.
        - Cleaned incoming students DataFrame.
        - DataFrame of removed local students with reasons.
        - DataFrame of removed incoming students with reasons.
    """

    local_students = local_students.copy()
    incoming_students = incoming_students.copy()

    if current_date is None:
        current_date = datetime.now()

    local_students['reason'] = local_students.apply(lambda row: filter_local_student(row, current_date), axis=1)
    incoming_students['reason'] = incoming_students.apply(lambda row: filter_incoming_student(row, current_date), axis=1)

    removed_local_students: pd.DataFrame = local_students.loc[local_students['reason'].notna()]
    removed_incoming_students: pd.DataFrame = incoming_students.loc[incoming_students['reason'].notna()]

    local_students = local_students.loc[local_students['reason'].isna()]
    incoming_students = incoming_students.loc[incoming_students['reason'].isna()]

    local_students = local_students.drop(columns=['reason'])
    incoming_students = incoming_students.drop(columns=['reason'])

    return local_students, incoming_students, removed_local_students, removed_incoming_students
