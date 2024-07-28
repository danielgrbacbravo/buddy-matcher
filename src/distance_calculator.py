import configparser
import pandas as pd
import datetime
import math
import  numpy as np
from munkres import Munkres, DISALLOWED

def calculate_age_distance(
  config: configparser.ConfigParser,
  age_range: int,
  local_students: pd.Series,
  incoming_student: pd.Series) -> float:
    """Calculate the age distance between a local student and an incoming student.

    This function computes the absolute difference in ages between the two students,
    adjusts it based on a desired age difference from the configuration, and scales
    the result using the factorial of the age difference and the provided age range.

    :param config: A ConfigParser object containing configuration parameters, including the desired age difference.
    :param age_range: An integer representing the range of ages used for scaling the distance.
    :param local_students: A pandas Series representing the local student's attributes, including their age.
    :param incoming_student: A pandas Series representing the incoming student's attributes, including their age.
    :return: A float representing the scaled distance between the ages of the two students.
    """
    local_age = local_students['Age']
    incoming_age = incoming_student['Age']

    age_difference = abs(int(local_age) - int(incoming_age))

    age_difference -= int(config.get('parameters', 'desired_age_difference'))

    # Scale age difference using factorial
    age_difference_distance = math.factorial(age_difference) if age_difference > 0 else 0

    # age_difference_distance /= (math.factorial(self.age_range) * age_multiplier)
    age_difference_distance = float(age_difference_distance / (math.factorial(age_range)))

    return age_difference_distance


def calculate_gender_distance(
  config: configparser.ConfigParser,
  gender_range: int,
  local_students: pd.Series,
  incoming_students: pd.Series) -> float:
    """Function to calculate the distance between the gender preferences of local and incoming students.

    This function evaluates the gender preferences of both local and incoming students and calculates a
    distance metric based on any penalties associated with mismatched preferences. The distance is scaled
    by the provided gender_range.

    :param config: A ConfigParser object containing configuration parameters including gender preference penalties.
    :param gender_range: An integer representing the range of gender preferences used for scaling the distance.
    :param local_students: A pandas Series representing the local student's attributes, including their gender preference.
    :param incoming_students: A pandas Series representing the incoming student's attributes, including their gender preference.
    :return: A float representing the calculated distance based on gender preferences.
    """

    distance: float = 0
    local_gender_preference_penalty = int(config.get('parameters', 'local_gender_preference_penalty'))
    incoming_gender_preference_penalty = int(config.get('parameters', 'incoming_gender_preference_penalty'))

    if local_students['GenderPreference'] != 'Mix/No preference' and local_students['GenderPreference'] != \
            incoming_students['Gender']:
        distance += local_gender_preference_penalty

    if incoming_students['GenderPreference'] != 'No preference' and incoming_students['GenderPreference'] != \
            local_students['Gender']:
        distance += incoming_gender_preference_penalty

    distance = float(distance / gender_range)

    return distance



def calculate_age_gender_distance(
  config: configparser.ConfigParser,
  age_range: int,
  local_students: pd.Series,
  incoming_students: pd.Series) -> float:
    """Calculate the distance between the ages and genders of a local student and an incoming student.

    This function evaluates the age and gender of both students. If the genders are different and the absolute
    age difference exceeds the desired age difference specified in the configuration, a distance of 1.0 is returned.
    Otherwise, the distance remains 0.0.

    :param config: A ConfigParser object containing configuration parameters, including the desired age difference.
    :param age_range: An integer representing the range of ages used for scaling the distance (not used in this function).
    :param local_students: A pandas Series representing the local student's attributes, including their age and gender.
    :param incoming_students: A pandas Series representing the incoming student's attributes, including their age and gender.
    :return: A float representing the calculated distance based on age and gender.
    """

    distance = 0.0
    local_age = local_students['Age']
    local_gender = local_students['Gender']
    incoming_age = incoming_students['Age']
    incoming_gender = incoming_students['Gender']

    if local_gender != incoming_gender:
        if abs(local_age - incoming_age) > int(config.get('parameters', 'desired_age_difference')):
            distance = 1.0

    return distance


def calculate_university_distance(local_students: pd.Series, incoming_students: pd.Series) -> float:
  """Function to calculate the distance between the universities of two students.

  This function compares the universities of the local and incoming students. If the universities are different,
  a distance of 1.0 is returned; otherwise, the distance is 0.0.

  :param local_students: A pandas Series representing the local student's attributes, including their university.
  :param incoming_students: A pandas Series representing the incoming student's attributes, including their university.
  :return: A float representing the calculated distance based on the universities of the two students.
  """

  if local_students['University'] != incoming_students['University']:
      return 1.0
  return 0.0


def calculate_faculty_distance(local_students: pd.Series, incoming_students: pd.Series, faculty_distances: pd.DataFrame) -> float:
  """Calculate the distance between the faculties of a local student and an incoming student.

  This function compares the faculty of the local student with that of the incoming student. If the faculties are
  different, the distance is determined based on pre-defined distances stored in the faculty_distances DataFrame.
  If the faculties are the same, the distance is 0.0.

  :param local_students: A pandas Series representing the local student's attributes, including their faculty.
  :param incoming_students: A pandas Series representing the incoming student's attributes, including their faculty.
  :param faculty_distances: A pandas DataFrame containing the distances between different faculties.
  :return: A float representing the calculated distance between the faculties of the two students.
  """

  distance: float = 0.0
  local_faculty = local_students['Faculty']
  incoming_faculty = incoming_students['Faculty']

  if local_faculty != incoming_faculty:
      distance = float(faculty_distances[local_faculty].loc[incoming_faculty])
  return distance


def calculate_personal_interests_distance(
  config: configparser.ConfigParser,
  local_students: pd.Series,
  incoming_students: pd.Series,
  hobby_range: int,
  hobbies: pd.DataFrame) -> float:
  """Calculate the distance based on the personal interests (hobbies) of local and incoming students.

  This function computes a distance metric based on the differences in hobbies between local and incoming students.
  Each hobby is weighted by a factor specified in the configuration, which allows for different levels of importance
  for each hobby. The resulting distance is normalized by the provided hobby range.

  :param config: A ConfigParser object containing configuration parameters including hobby weights.
  :param local_students: A pandas Series representing the local student's attributes, including their hobbies.
  :param incoming_students: A pandas Series representing the incoming student's attributes, including their hobbies.
  :param hobby_range: An integer representing the range of hobbies used for scaling the distance.
  :param hobbies: A pandas DataFrame containing the list of hobbies being compared.
  :return: A float representing the calculated distance based on the personal interests of the two students.
  """
  distance = 0
  for hobby in hobbies:
    hobby_factor = float(config.get('hobbies', hobby))
    distance += abs(local_students[hobby] - incoming_students[hobby]) * hobby_factor

  distance /= hobby_range
  return float(distance)



def calculate_availability_distance(local_student: pd.Series, incoming_student: pd.Series, date_range: int) -> float:
  availability =  pd.to_datetime(local_student['Availability'])
  arrival  = pd.to_datetime(incoming_student['Arrival'])

  days_difference: float  = (availability - arrival).days

  # If the local student is available before the incoming student, the result will be below 0
  if days_difference >= 0:
      days_difference = float(days_difference / date_range)
      return days_difference

  return 0.0






def calculate_text_availability_distance(
  config: configparser.ConfigParser,
  local_student: pd.Series,
  incoming_student: pd.Series) -> float:
  """Calculate the distance based on the text availability date of a local student and the arrival date of an incoming student.

  This function computes the distance between the availability date of the local student (provided as a string in the format 'YYYY-MM-DD')
  and the arrival date of the incoming student (also provided as a string in the same format). The distance is calculated based on the
  ideal difference in days specified in the configuration. If the arrival date is later than the availability date by at least the
  ideal difference, a distance of 0 is returned. If the arrival date is earlier than or the same as the availability date, a distance
  of 100 is returned. Otherwise, a penalty is calculated based on how far the arrival date is from the ideal difference.

  :param config: A ConfigParser object containing configuration parameters, including the desired date difference.
  :param local_student: A pandas Series representing the local student's attributes, including their availability date.
  :param incoming_student: A pandas Series representing the incoming student's attributes, including their arrival date.
  :return: A float representing the calculated distance based on the availability dates of the two students.
  """

  # assuming local_student['AvailabilityText'] is a string in the format 'YYYY-MM-DD'
  # and incoming_student['Arrival'] is a string in the format 'YYYY-MM-DD'
  local_student_text_date = pd.to_datetime(local_student['AvailabilityText'])
  incoming_student_arrival_date = pd.to_datetime(incoming_student['Arrival'])

  ideal_difference = float(config.get('parameters', 'desired_date_difference'))

  if (incoming_student_arrival_date - local_student_text_date).days >= ideal_difference:
      return 0
  elif (incoming_student_arrival_date - local_student_text_date).days <= 0:
      return 100
  else:
      days_between = (incoming_student_arrival_date - local_student_text_date).days

      penalty: float  = float(ideal_difference - days_between)
      penalty = float(penalty / ideal_difference)
      return penalty


def calculate_meeting_frequency_distance(
  local_student: pd.Series,
  incoming_student: pd.Series,
  meeting_frequency_range: int) -> float:
  """Calculate the distance based on the meeting frequency preferences of a local student and an incoming student.

  This function computes the absolute difference between the meeting frequencies of the two students and normalizes
  the result by the provided meeting frequency range. The resulting distance indicates how closely aligned the students'
  preferences are regarding how often they would like to meet.

  :param local_student: A pandas Series representing the local student's attributes, including their meeting frequency.
  :param incoming_student: A pandas Series representing the incoming student's attributes, including their meeting frequency.
  :param meeting_frequency_range: An integer representing the range of meeting frequencies used for scaling the distance.
  :return: A float representing the calculated distance based on the meeting frequency preferences of the two students.
  """

  local_meeting_frequency: float  = float(local_student['MeetFrequency'])
  incoming_meeting_frequency: float  = float(incoming_student['MeetFrequency'])

  distance: float  = abs(local_meeting_frequency - incoming_meeting_frequency)
  distance /= meeting_frequency_range
  return distance


def calculate_expectation_distance(
  local_student: pd.Series,
  incoming_student: pd.Series,
  ) -> float:

  distance: float = 0.0

  local_expectations = [int(expectation in local_student['Expectations']) for expectation in
                        ['Just answering some (practical) questions', 'Showing the new student(s) around',
                          'Becoming friends with my buddies']]

  incoming_expectations = [int(expectation in incoming_student['Expectations']) for expectation in
                            ['Just asking (practical) questions', 'Being shown around the city',
                            'Becoming friends with my buddy']]

  comparison: list[int] = [0 if x == y else 1 for x, y in zip(local_expectations, incoming_expectations)]

  count_ones: int = comparison.count(1)
  distance = count_ones / len(comparison)

  return distance




def _distance(self, local_student_index: int, incoming_student_index: int):
    """Function to calculate the distance between two students
    :param local_student_index: The index of the local student
    :param incoming_student_index: The index of the incoming student
    :return: The distance between the two students
    """
    distance = 0

    # Obtain the two students
    local_student = self.local_students_copy.iloc[local_student_index]
    incoming_student = self.incoming_students_copy.iloc[incoming_student_index]

    self.deny_list.columns = self.deny_list.columns.str.strip().str.replace("''", '').str.replace("'", '')

    # Make sure these students aren't in the deny list
    if ((self.deny_list['Email Local'] == local_student['Email']) & (
            self.deny_list['Email Incoming'] == incoming_student['Email'])).any():
        return DISALLOWED

    if max((local_student['Availability'] - incoming_student['Arrival']).days, 0) > float(
            self.configs.get('parameters', 'maximum_unavailable_duration')):
        distance += 100

    # Get all factors
    age_factor = float(self.configs.get('normalization', 'age_factor'))
    gender_factor = float(self.configs.get('normalization', 'gender_factor'))
    age_gender_factor = float(self.configs.get('normalization', 'age_gender_factor'))
    university_factor = float(self.configs.get('normalization', 'university_factor'))
    faculty_factor = float(self.configs.get('normalization', 'faculty_factor'))
    interests_factor = float(self.configs.get('normalization', 'interests_factor'))
    availability_text_factor = float(self.configs.get('normalization', 'availability_text_factor'))
    availability_physical_factor = float(self.configs.get('normalization', 'availability_physical_factor'))
    meeting_frequency_factor = float(self.configs.get('normalization', 'meeting_frequency_factor'))
    expectation_factor = float(self.configs.get('normalization', 'expectations_factor'))

    # Multiple Factors by their respective distances
    distance += (age_factor * self._age_distance(local_student, incoming_student))
    distance += (gender_factor * self._gender_distance(local_student, incoming_student))
    distance += (age_gender_factor * self._age_gender_distance(local_student, incoming_student))
    distance += (university_factor * self._university_distance(local_student, incoming_student))
    distance += (faculty_factor * self._faculty_distance(local_student, incoming_student))
    distance += (interests_factor * self._interests_distance(local_student, incoming_student))

    distance += (availability_physical_factor * self._availability_physical_distance(local_student, incoming_student))

    try:
        distance += (availability_text_factor * self._availability_text_distance(local_student, incoming_student))
    except TypeError:
        # Catch the possibility that this is a DISSALOWED match because of availability to text
        return DISALLOWED

    distance += (meeting_frequency_factor * self._meeting_frequency_distance(local_student, incoming_student))
    distance += (expectation_factor * self._expectation_distance(local_student, incoming_student))

    return distance
