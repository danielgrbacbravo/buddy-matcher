#!/usr/bin/env python3


# Importing external libraries
import configparser
from datetime import datetime
from typing import Dict
import pandas as pd
import os
from pandas.core.arrays.datetimelike import Union
import pyfiglet
import numpy as np
import colorlog as logging
# Importing internal libraries
import distance_calculator
import formatter
import student_filter
import normalization_calculator
import outlier_calculator
import formatter
import student_matcher
import report


def main():

  logging.basicConfig(level=logging.INFO)

  # figlet name
  custom_fig = pyfiglet.Figlet(font='standard')
  print(custom_fig.renderText('ESN Buddy Matcher'))

  output_dir: str = 'output'

  # Check if the input files exist
  if not os.path.exists("/input/local_students.csv"):
      raise FileNotFoundError(f"Local students file not found in the input folder.")

  logging.info("Local students file found")

  if not os.path.exists("/input/incoming_students.csv"):
      raise FileNotFoundError(f"Incoming students file not found in the input folder.")

  logging.info("Incoming students file found")

  # Load the data
  local_students: pd.DataFrame = pd.read_csv("/input/local_students.csv")
  logging.info("Local students loaded [%s]", local_students.shape)

  incoming_students: pd.DataFrame = pd.read_csv("/input/incoming_students.csv")
  logging.info("Incoming students loaded [%s]", incoming_students.shape)

  try:
        hobbies: pd.DataFrame = pd.read_csv("/config/hobbies.csv", quotechar="'").iloc[:, 0].tolist()
        logging.info("Hobbies loaded")

  except FileNotFoundError as e:
          print(f"Error reading hobbies file: {e}\nEnsure there is a hobbies.csv file at the given path")
          exit()

  try:
      faculty_distances: pd.DataFrame = pd.read_excel(r'/config/faculty_distances.xlsx', index_col=0)
  except FileNotFoundError as e:
      print(f"Error reading faculty distances file: {e}\nEnsure there is a faculty_distances.xlsx file in the ")
      exit()


  logging.info("Faculty distances loaded")


  # Clean column names by replacing double single quotes with double quotes and stripping whitespace
  local_students.columns = local_students.columns.str.replace("''", '"').str.strip()
  incoming_students.columns = incoming_students.columns.str.replace("''", '"').str.strip()
  logging.info("Columns cleaned")

    # Remap the columns in the dataframes for consistency
  column_mapping: Dict[str, str] = formatter.read_column_mapping("/config/local_students_column_renames.csv")
  local_students = formatter.remap_columns(column_mapping,local_students)

  column_mapping = formatter.read_column_mapping("/config/incoming_students_column_renames.csv")
  incoming_students = formatter.remap_columns(column_mapping,incoming_students)
  logging.info("Columns remapped successfully")

  # Convert all date columns to datetime objects
  local_students, incoming_students = formatter.convert_all_dates_to_datetime(local_students, incoming_students)





  logging.info("Dates converted to datetime objects successfully")

  local_students, incoming_students = formatter.rename_timestamps(local_students, incoming_students)
  logging.info("Timestamps renamed")

  local_students, incoming_students, removed_local_students, removed_incoming_students = student_filter.apply_filters(local_students, incoming_students)
  logging.info("Filters applied")


  # Strip spaces from column names
  local_students.columns = local_students.columns.str.strip()
  incoming_students.columns = incoming_students.columns.str.strip()

  local_students, incoming_students = formatter.drop_irrelevant_columns(local_students, incoming_students)
  logging.info("Irrelevant columns dropped")

    #adjust dates
  current_date = datetime.now()
  formatter.adjust_dataframe_dates(local_students, ['Availability', 'AvailabilityText'], current_date)
  formatter.adjust_dataframe_dates(incoming_students, ['Arrival'], current_date)

  threshold: float = 2.0

  # look for outliers by age in the incoming students
  local_std: float = float(local_students['Age'].std())
  incoming_outliers = outlier_calculator.calculate_outliers(incoming_students, threshold=threshold, std= local_std)

  logging.info("Outliers calculated")
  are_outliers: bool = any(incoming_outliers)

  if are_outliers:

    logging.warning("Outliers found in incoming students using a threshold of %i and a STD of %s", threshold, local_std)
    str_outlier = outlier_calculator.outliers_to_str(incoming_students, incoming_outliers)
    for i in str_outlier:
       #print in red color
       print(f"\033[91m{i}\033[00m")
    logging.info("Outliers printed")

    logging.info("running the program without the outliers")


    # create dulicate copies of the incoming and local students
    local_students_no_outliers: pd.DataFrame= local_students.copy()
    incoming_students_no_outliers: pd.DataFrame = incoming_students.copy()
    logging.info("Copies of incoming and local students created")

    #remove outliers
    incoming_students_no_outliers = outlier_calculator.remove_outliers(
      incoming_students_no_outliers
      , incoming_outliers)

    # Fix the indexes after removing people
    incoming_students_no_outliers.reset_index(drop=True, inplace=True)
    logging.info("Outliers removed from incoming students")

    # convert categories to numerical values
    local_students_no_outliers, incoming_students_no_outliers= formatter.convert_categories_to_numerical(
    local_students_no_outliers,
    incoming_students_no_outliers,
    hobbies)
     # calulate capacities of the local students and number of  incoming students
    base_local_capacity: int  = formatter.get_base_capacities(local_students_no_outliers)
    base_incoming_necessity: int = formatter.get_base_necessity(incoming_students_no_outliers)


    logging.info("Base capacities and necessities calculated")

    logging.info("base local capacity: %s", base_local_capacity)
    logging.info("base incoming necessity: %s", base_incoming_necessity)

    if base_local_capacity < base_incoming_necessity:
      logging.warning("The base local capacity is less than the base incoming necessity")
      logging.warning("The algorithm may not be able to match all incoming students")


    # compute the bounds for the different categories
    config = configparser.ConfigParser()
    config.read("/config/config.ini")
    normal_dict: Dict[str, Union[float,int]] = normalization_calculator.compute_normalization_values(
      local_students_no_outliers,
      incoming_students_no_outliers,
      config,
      hobbies,
      faculty_distances)
    logging.info("Normalization values computed")

    for key, value in normal_dict.items():
      logging.info("value for %s: %s", key, value)


    distance_matrix: pd.DataFrame = distance_calculator.caculate_student_distances(
    local_students_no_outliers,
    incoming_students_no_outliers,
    config,
    normal_dict,
    faculty_distances,
    hobbies)

    logging.info("Distance matrix computed")

    logging.info("beggining the Kuhn-Munkres algorithm for building the matching matrix")
    matching_matrix: pd.DataFrame = student_matcher.compute_optimal_pairs(distance_matrix, local_students_no_outliers, incoming_students_no_outliers, base_local_capacity, base_incoming_necessity)

    print(matching_matrix)

    logging.info("Matching matrix computed")
    # create the output dir
    os.makedirs(output_dir, exist_ok=True)
    # create the output file name
    file_name = f"matching_report_no_outliers{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"
    output_file_name = os.path.join(output_dir, file_name)

    report.create_report(matching_matrix, distance_matrix, local_students_no_outliers, incoming_students_no_outliers,  output_file_name)


  else:
    logging.info("No outliers found in incoming students using a threshold of %i and a STD of %s", threshold, local_std)


  logging.info("running the program without the outliers")


  # convert categories to numerical values
  local_students, incoming_students = formatter.convert_categories_to_numerical(
  local_students,
  incoming_students,
  hobbies)
    # calulate capacities of the local students and number of  incoming students
  base_local_capacity: int  = formatter.get_base_capacities(local_students)
  base_incoming_necessity: int = formatter.get_base_necessity(incoming_students)


  logging.info("Base capacities and necessities calculated")

  logging.info("base local capacity: %s", base_local_capacity)
  logging.info("base incoming necessity: %s", base_incoming_necessity)

  if base_local_capacity < base_incoming_necessity:
    logging.warning("The base local capacity is less than the base incoming necessity")
    logging.warning("The algorithm may not be able to match all incoming students")


    # compute the bounds for the different categories
  config = configparser.ConfigParser()
  config.read("/config/config.ini")
  normal_dict: Dict[str, Union[float,int]] = normalization_calculator.compute_normalization_values(
    local_students,
    incoming_students,
    config,
    hobbies,
    faculty_distances)
  logging.info("Normalization values computed")


  for key, value in normal_dict.items():
    logging.info("value for %s: %s", key, value)

  distance_matrix: pd.DataFrame = distance_calculator.caculate_student_distances(
  local_students,
  incoming_students,
  config,
  normal_dict,
  faculty_distances,
  hobbies)

  logging.info("Distance matrix computed")


  logging.info("beggining the Kuhn-Munkres algorithm for building the matching matrix")
  matching_matrix: pd.DataFrame = student_matcher.compute_optimal_pairs(distance_matrix, local_students, incoming_students, base_local_capacity, base_incoming_necessity)


  # create the output dir
  os.makedirs(output_dir, exist_ok=True)
  # create the output file name
  file_name = f"matching_report_with_outliers{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"
  output_file_name = os.path.join(output_dir, file_name)

  report.create_report(matching_matrix, distance_matrix, local_students, incoming_students,  output_file_name)


if __name__ == '__main__':
  main()
