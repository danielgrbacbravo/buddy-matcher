import format_check
import pandas as pd
import colorlog as logging
from typing import Tuple

def convert_all_dates_to_datetime(local_students: pd.DataFrame, incoming_students: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
  # Convert date columns to datetime objects and extract the date

  date_format: str = format_check.determine_datetime_format(local_students['Availability'].iloc[0])
  if date_format == "Unknown format":
    logging.error("Date format not recognized for Availability Date Column. Please check the date format in the input file.")
    raise ValueError("Date format not recognized. Please check the date format in the input file.")

  logging.info(f"Date format found for Availability Column: {date_format}")

  local_students['Availability'] = pd.to_datetime(
      local_students['Availability'], errors='coerce', format=date_format).dt.date




  date_format = format_check.determine_datetime_format(local_students['AvailabilityText'].iloc[0])
  if date_format == "Unknown format":
    logging.error("Date format not recognized for AvailabilityText Date Column. Please check the date format in the input file.")
    raise ValueError("Date format not recognized. Please check the date format in the input file.")

  logging.info(f"Date format found for AvailabilityText Column: {date_format}")

  local_students['AvailabilityText'] = pd.to_datetime(
      local_students['AvailabilityText'],
      errors='coerce', format=date_format).dt.date





  date_format = format_check.determine_datetime_format(incoming_students['Arrival'].iloc[0])
  if date_format == "Unknown format":
    logging.error("Date format not recognized for Arrival Date Colum. Please check the date format in the input file.")
    raise ValueError("Date format not recognized. Please check the date format in the input file.")

  logging.info(f"Date format found for Arrival Column: {date_format}")

  incoming_students['Arrival'] = pd.to_datetime(
      incoming_students['Arrival'], errors='coerce', format=date_format).dt.date

  return local_students, incoming_students


def rename_timestamps(local_students: pd.DataFrame, incoming_students: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Renames the first column of both local and incoming students DataFrames to 'Timestamp'.

    Args:
        local_students (pd.DataFrame): DataFrame containing local students' data.
        incoming_students (pd.DataFrame): DataFrame containing incoming students' data.

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: A tuple containing the DataFrames with renamed first columns.
    """
    local_students = local_students.copy()
    incoming_students = incoming_students.copy()

    first_column_name_local = str(local_students.columns[0])
    first_column_name_incoming = str(incoming_students.columns[0])
    local_students.rename(columns={first_column_name_local: "Timestamp"}, inplace=True)
    incoming_students.rename(columns={first_column_name_incoming: "Timestamp"}, inplace=True)
    return local_students, incoming_students
