#import external libraries
from typing import Dict
from typing import List
import pandas as pd
from typing import Tuple
from typing import Optional
from datetime import datetime, timedelta
import configparser
import numpy as np
from typing import Union



def create_deny_list() -> pd.DataFrame:
    """Creates an empty DataFrame with columns 'Email Local' and 'Email Incoming'."""
    deny_list = pd.DataFrame({'Email Local': pd.Series(dtype='str'), 'Email Incoming': pd.Series(dtype='str')})
    return deny_list



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


def does_configuration_exist() -> bool:
  try:
    config = configparser.ConfigParser()
    config.read('config.ini')
    return True
  except FileNotFoundError:
    return False


def generate_cleaned_dataframes(
        local_students: pd.DataFrame,
        incoming_students: pd.DataFrame,
        faculty_distances: Optional[pd.DataFrame],
        local_students_irrelevant_columns: Optional[pd.DataFrame],
        incoming_students_irrelevant_columns: Optional[pd.DataFrame]
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Generates cleaned DataFrames for local and incoming students.

    Args:
        local_students (pd.DataFrame): DataFrame containing local students' data.
        incoming_students (pd.DataFrame): DataFrame containing incoming students' data.
        faculty_distances (Optional[pd.DataFrame]): DataFrame containing distances between faculties. Defaults to None.
        local_students_irrelevant_columns (Optional[pd.DataFrame]): DataFrame containing irrelevant columns for local students. Defaults to None.
        incoming_students_irrelevant_columns (Optional[pd.DataFrame]): DataFrame containing irrelevant columns for incoming students. Defaults to None.

    """
    local_students = local_students.copy()
    incoming_students = incoming_students.copy()

    if does_configuration_exist() is False:
        raise FileNotFoundError('Configuration file not found. Please run the configuration script first.')

    if faculty_distances is None:
      try:
        faculty_distances = pd.read_excel('config/faculty_distances.xlsx')
      except FileNotFoundError as e:
        print('Faculty distances file not found. Please run the configuration script first.')
        raise e

    if local_students_irrelevant_columns is None:
      try:
        local_students_irrelevant_columns = pd.read_csv(r'config/local_students_irrelevant_columns.csv',
                                                     quotechar="'")
      except FileNotFoundError as e:
        print('Local students irrelevant columns file not found. Please run the configuration script first.')
        raise e

    if incoming_students_irrelevant_columns is None:
      try:
        incoming_students_irrelevant_columns = pd.read_csv(r'config/incoming_students_irrelevant_columns.csv',
                                                        quotechar="'")
      except FileNotFoundError as e:
        print('Incoming students irrelevant columns file not found. Please run the configuration script first.')
        raise e

    # Strip spaces from column names
    local_students.columns = local_students.columns.str.strip()
    incoming_students.columns = incoming_students.columns.str.strip()

    # Make copies of the original DataFrames
    local_students_copy = local_students.copy(deep=True)
    incoming_students_copy = incoming_students.copy(deep=True)

    # Convert the DataFrame of columns to drop into a list
    local_students_columns_to_drop = local_students_irrelevant_columns.iloc[:, 0].tolist()
    incoming_students_columns_to_drop = incoming_students_irrelevant_columns.iloc[:, 0].tolist()

    # Drop the specified columns
    local_students_copy = local_students_copy.drop(columns=local_students_columns_to_drop)
    incoming_students_copy = incoming_students_copy.drop(columns=incoming_students_columns_to_drop)

    return local_students_copy, incoming_students_copy





def read_column_mapping(filename: str) -> Dict[str,str]:
    """Reads the column mapping from the configuration file.
    Returns:
        Dict[str,str]: Dictionary containing the mapping of old column names to new column names.
    """

    try:
        column_mapping = pd.read_csv(filename, quotechar="'", skipinitialspace=True)
    except FileNotFoundError as e:
        print('Column mapping file not found. Please run the configuration script first.')
        raise e

    column_mapping.columns = column_mapping.columns.str.strip()
    column_mapping_dict = dict(zip(column_mapping['Old Name'], column_mapping['New Name']))
    return column_mapping_dict





def remap_columns(mapping_dict: Dict[str,str], Dataframe: pd.DataFrame) -> pd.DataFrame:
    """Remaps columns in a DataFrame based on a mapping dictionary.

    Args:
        mapping_dict (Dict[str,str]): Dictionary containing the mapping of old column names to new column names.
        Dataframe (pd.DataFrame): DataFrame to remap columns.

    Returns:
        pd.DataFrame: DataFrame with remapped columns.
    """

    Dataframe = Dataframe.copy()

    Dataframe = Dataframe.rename(columns=mapping_dict)
    return Dataframe





def convert_categories_to_numerical(local_students_df: pd.DataFrame,
                                    incoming_students_df: pd.DataFrame,
                                    hobbies: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Convert categorical hobby and frequency interests into numerical values
    for easier comparison.

    Parameters:
    local_students_df (pd.DataFrame): DataFrame containing local student data.
    incoming_students_df (pd.DataFrame): DataFrame containing incoming student data.
    hobbies_file_path (str): Path to the CSV file containing the list of hobbies.

    Returns:
    Tuple[pd.DataFrame, pd.DataFrame]: A tuple containing the modified local_students_df
    and incoming_students_df DataFrames.
    """

    local_students_df = local_students_df.copy()
    incoming_students_df = incoming_students_df.copy()

    hobby_options = ['Not interested', 'Interests me a little', 'Very interested']
    hobby_options_replacement = list(range(len(hobby_options)))

    for hobby in hobbies:
        if hobby in local_students_df.columns:
            local_students_df[hobby] = local_students_df[hobby].replace(hobby_options, hobby_options_replacement).infer_objects(copy=False)
        if hobby in incoming_students_df.columns:
            incoming_students_df[hobby] = incoming_students_df[hobby].replace(hobby_options, hobby_options_replacement).infer_objects(copy=False)

    frequency_options = ['One time only', 'Once a month', 'Twice a month', 'Once a week or more']
    frequency_options_replacement = list(range(len(frequency_options)))

    if 'MeetFrequency' in local_students_df.columns:
        local_students_df['MeetFrequency'] = local_students_df['MeetFrequency'].replace(frequency_options, frequency_options_replacement).infer_objects(copy=False)
    if 'MeetFrequency' in incoming_students_df.columns:
        incoming_students_df['MeetFrequency'] = incoming_students_df['MeetFrequency'].replace(frequency_options, frequency_options_replacement).infer_objects(copy=False)

    return local_students_df, incoming_students_df





def adjust_dates(date: Union[str, datetime], current_date: datetime) -> datetime:
    parsed_date = pd.to_datetime(date).to_pydatetime()
    return parsed_date if parsed_date > current_date else current_date






def adjust_dataframe_dates(dataframe: pd.DataFrame, columns: List[str], current_date: datetime) -> None:
    dataframe = dataframe.copy()
    adjust_dates_vectorized = np.vectorize(adjust_dates)
    for column in columns:
        dataframe[column] = adjust_dates_vectorized(pd.to_datetime(dataframe[column]), current_date)






def get_base_capacities(local_students: pd.DataFrame) -> int:
    """Function to get the base capacities of the local students and the necessity of incoming students"""
    base_local_capacity: int = int(local_students['Capacity'].sum())
    return base_local_capacity






def get_base_necessity(incoming_students: pd.DataFrame) -> int:
    """Function to get the base necessity of incoming students"""
    base_necessity: int = int(incoming_students.count(axis=1).count())
    return base_necessity
