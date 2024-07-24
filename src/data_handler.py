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
    print("constructing empty deny list")
    deny_list = pd.DataFrame({'Email Local': pd.Series(dtype='str'), 'Email Incoming': pd.Series(dtype='str')})
    return deny_list





def clean_data(local_students: pd.DataFrame, incoming_students: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Cleans the data for local and incoming students DataFrames.

    This function performs the following operations:
    1. Replaces double single quotes with double quotes in column names.
    2. Strips leading and trailing whitespace from column names.
    3. Converts specific date columns to datetime objects and extracts the date.

    Args:
        local_students (pd.DataFrame): DataFrame containing local students' data.
        incoming_students (pd.DataFrame): DataFrame containing incoming students' data.

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: A tuple containing the cleaned DataFrames for local and incoming students.
    """

    # Clean column names by replacing double single quotes with double quotes and stripping whitespace
    local_students.columns = local_students.columns.str.replace("''", '"').str.strip()
    incoming_students.columns = incoming_students.columns.str.replace("''", '"').str.strip()

    # Convert date columns to datetime objects and extract the date
    local_students[
        'From approximately which date are you available to physically meet your buddy match?'] = pd.to_datetime(
        local_students['From approximately which date are you available to physically meet your buddy match?'], errors='coerce', format='%d/%m/%Y').dt.date
    local_students[
        'From approximately which date are you available to answer questions from your buddy match? (through mail, phone, whatsapp etc.)'] = pd.to_datetime(
        local_students[
            'From approximately which date are you available to answer questions from your buddy match? (through mail, phone, whatsapp etc.)'],
        errors='coerce', format='%d/%m/%Y').dt.date

    incoming_students['When will you arrive in Groningen (approximately)?'] = pd.to_datetime(
        incoming_students['When will you arrive in Groningen (approximately)?'], errors='coerce', format='%d-%m-%Y').dt.date

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
    first_column_name_local = str(local_students.columns[0])
    first_column_name_incoming = str(incoming_students.columns[0])
    local_students.rename(columns={first_column_name_local: "Timestamp"}, inplace=True)
    incoming_students.rename(columns={first_column_name_incoming: "Timestamp"}, inplace=True)
    return local_students, incoming_students





def filter_incoming_student(row: pd.Series, current_date: Optional[datetime] = None) -> str | None:
    """
    Filters incoming students based on their arrival date and accessibility requirements.

    Args:
        row (pd.Series): A row of the incoming students DataFrame.
        current_date (Optional[datetime]): The current date to compare with. Defaults to None, in which case the current date is used.

    Returns:
        str | None: A string indicating the reason for filtering out the student, or None if the student passes the filter.
    """
    date_arriving = pd.to_datetime(row['When will you arrive in Groningen (approximately)?'], format='%d/%m/%Y')

    three_months_from_now = (current_date or datetime.now()) + timedelta(days=90)

    if date_arriving < datetime.now():
        row.loc['When will you arrive in Groningen (approximately)?'] = datetime.today()
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
        row['From approximately which date are you available to physically meet your buddy match?'],
        format='%d/%m/%Y')

    three_months_from_now = (current_date or datetime.now()) + timedelta(days=90)

    if date_available is pd.NaT:
        return 'Date not entered correctly - reformat and read to input'

    if date_available < datetime.now():
        row.loc[
            'From approximately which date are you available to physically meet your buddy match?'] = datetime.today()
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

    print('Filtering local and incoming students')

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






def compute_age_range(local_students: pd.DataFrame, incoming_students: pd.DataFrame) -> int:
    max_local_age: float = float(local_students['Age'].max())
    max_incoming_age: float  = float(incoming_students['Age'].max())

    min_local_age: float  = float(local_students['Age'].min())
    min_incoming_age: float = float(incoming_students['Age'].min())

    max_age: Union[int, float] = max(max_local_age, max_incoming_age)
    min_age: Union[int, float] = min(min_local_age, min_incoming_age)

    age_range: int = int(max_age - min_age)
    return age_range


def compute_gender_range(configs: configparser.ConfigParser) -> int:
    local_gender_preference_penalty: int = int(configs.get('parameters', 'local_gender_preference_penalty'))
    incoming_gender_preference_penalty: int = int(configs.get('parameters', 'incoming_gender_preference_penalty'))

    gender_range: int = local_gender_preference_penalty + incoming_gender_preference_penalty
    return gender_range


def compute_hobby_range(configs: configparser.ConfigParser, hobbies: pd.DataFrame) -> float:
    hobby_range: float = 0.0
    for hobby in hobbies:
        hobby_range += (3 * float(configs.get('hobbies', hobby)))
    return hobby_range


def compute_meeting_frequency_range(local_students: pd.DataFrame, incoming_students: pd.DataFrame) -> float:
    max_local_meeting_frequency: float = float(local_students['MeetFrequency'].max())
    max_incoming_meeting_frequency: float = float(incoming_students['MeetFrequency'].max())

    min_local_meeting_frequency: float = float(local_students['MeetFrequency'].min())
    min_incoming_meeting_frequency: float = float(incoming_students['MeetFrequency'].min())

    max_meeting_frequency: float = max(max_local_meeting_frequency, max_incoming_meeting_frequency)
    min_meeting_frequency: float = min(min_local_meeting_frequency, min_incoming_meeting_frequency)

    meeting_frequency_range: float = max_meeting_frequency - min_meeting_frequency
    return meeting_frequency_range


def compute_date_range(local_students: pd.DataFrame, incoming_students: pd.DataFrame) -> int:
    # Convert the 'Availability' and 'Arrival' columns to datetime if they aren't already
    local_datetime = pd.to_datetime(local_students['Availability'], errors='coerce')
    incoming_datetime = pd.to_datetime(incoming_students['Arrival'], errors='coerce')

    max_local_availability_date: pd.Timestamp = local_datetime.max()
    min_local_availability_date: pd.Timestamp = incoming_datetime.min()

    max_incoming_arrival_date: pd.Timestamp =  local_datetime.max()
    min_incoming_arrival_date: pd.Timestamp =  incoming_datetime.min()

    max_dates: pd.Timestamp = max(max_local_availability_date, max_incoming_arrival_date)
    min_dates: pd.Timestamp = min(min_local_availability_date, min_incoming_arrival_date)

    date_range: int = (max_dates - min_dates).days
    return date_range


def compute_faculty_range(faculty_distances: pd.DataFrame) -> float:
    return float(faculty_distances.max().max())


def compute_normalization_values(
    local_students: pd.DataFrame,
    incoming_students: pd.DataFrame,
    configs: configparser.ConfigParser,
    hobbies: pd.DataFrame,
    faculty_distances: pd.DataFrame
) -> dict:
    """Computes normalization values for various parameters based on the provided DataFrames.

    This function calculates the following normalization values:
    - Age range: The difference between the maximum and minimum ages of local and incoming students.
    - Gender range: The penalty values for local and incoming gender preferences from the configuration.
    - Faculty range: The maximum distance between faculties.
    - Hobby range: The weighted sum of hobby preferences based on the configuration.
    - Meeting frequency range: The difference between the maximum and minimum meeting frequencies of local and incoming students.
    - Date range: The difference in days between the latest availability date and the earliest arrival date.

    Args:
        local_students_original (pd.DataFrame): The original DataFrame of local students.
        incoming_students_original (pd.DataFrame): The original DataFrame of incoming students.
        local_students_copy (pd.DataFrame): A copy of the DataFrame of local students after filtering.
        incoming_students_copy (pd.DataFrame): A copy of the DataFrame of incoming students after filtering.
        configs (configparser.ConfigParser): Configuration parser containing parameters for calculations.
        hobbies (list[str]): List of hobbies to consider for hobby range computation.
        faculty_distances (pd.DataFrame): DataFrame containing distances between faculties.

    Returns:
        dict: A dictionary containing computed normalization values for age range, gender range, faculty range,
              hobby range, meeting frequency range, and date range.
    """
    normalization_values = {
        'age_range': compute_age_range(local_students.copy(), incoming_students.copy()),
        'gender_range': compute_gender_range(configs),
        'faculty_range': compute_faculty_range(faculty_distances),
        'hobby_range': compute_hobby_range(configs, hobbies),
        'meeting_frequency_range': compute_meeting_frequency_range(local_students.copy(), incoming_students.copy()),
        'date_range': compute_date_range(local_students.copy(), incoming_students.copy())
    }
    return normalization_values
