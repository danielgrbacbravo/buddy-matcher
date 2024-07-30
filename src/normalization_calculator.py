import configparser
from typing import Dict, Union
import pandas as pd
import os

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
) -> dict[str, Union[int, float]]:
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
