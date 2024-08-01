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
import data_handler
import student_filter
import normalization_calculator
import outlier_calculator

def main():

  logging.basicConfig(level=logging.INFO)

  # figlet name of the project
  custom_fig = pyfiglet.Figlet(font='standard')
  print(custom_fig.renderText('ESN Buddy Matcher'))


  output_dir: str = 'output/run_final_matching_algorithm_' + datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

  # Check if the input files exist
  if not os.path.exists("input/local_students.csv"):
      raise FileNotFoundError(f"Local students file not found in the input folder.")

  if not os.path.exists("input/incoming_students.csv"):
      raise FileNotFoundError(f"Incoming students file not found in the input folder.")

  if not os.path.exists("input/deny_list.csv"):
    deny_list = data_handler.create_deny_list()
  else:
    deny_list = pd.read_csv("input/deny_list.csv")

  # Load the data
  local_students: pd.DataFrame = pd.read_csv("input/local_students.csv")
  logging.info("Local students loaded [%s]", local_students.shape)

  incoming_students: pd.DataFrame = pd.read_csv("input/incoming_students.csv")
  logging.info("Incoming students loaded [%s]", incoming_students.shape)

  try:
        hobbies: pd.DataFrame = pd.read_csv("config/hobbies.csv", quotechar="'").iloc[:, 0].tolist()
        logging.info("Hobbies loaded")

  except FileNotFoundError as e:
          print(f"Error reading hobbies file: {e}\nEnsure there is a hobbies.csv file at the given path")
          exit()

  try:
      faculty_distances: pd.DataFrame = pd.read_excel(r'config/faculty_distances.xlsx', index_col=0)
  except FileNotFoundError as e:
      print(f"Error reading faculty distances file: {e}\nEnsure there is a faculty_distances.xlsx file in the ")
      exit()


  logging.info("Faculty distances loaded")

  # clean and filter the data
  local_students, incoming_students = data_handler.clean_data(local_students, incoming_students)
  logging.info("Data cleaned")
  local_students, incoming_students = data_handler.rename_timestamps(local_students, incoming_students)
  logging.info("Timestamps renamed")
  local_students, incoming_students, removed_local_students, removed_incoming_students = student_filter.apply_filters(local_students, incoming_students)
  logging.info("Filters applied")

  # clean dataframes
  local_students, incoming_students = data_handler.generate_cleaned_dataframes(local_students, incoming_students, None,None,None)
  logging.info("Dataframes cleaned")

  # Remap the columns in the dataframes for consistency
  column_mapping: Dict[str, str] = data_handler.read_column_mapping("config/local_students_column_renames.csv")
  local_students = data_handler.remap_columns(column_mapping,local_students)

  column_mapping = data_handler.read_column_mapping("config/incoming_students_column_renames.csv")
  incoming_students = data_handler.remap_columns(column_mapping,incoming_students)
  logging.info("Columns remapped")


  # look for outliers by age in the incoming students

  local_std: float = float(local_students['Age'].std())
  incoming_outliers = outlier_calculator.calculate_outliers(incoming_students, threshold=2.0, std= local_std)
  str_outlier: list[str] = outlier_calculator.outliers_to_str(incoming_students, incoming_outliers)
  logging.warning("Outliers found in incoming students using a threshold of %i and a STD of %s", 2.0, local_std)
  for i in str_outlier:
    #print in red color
    print(f"\033[91m{i}\033[00m")

  # convert categories to numerical values
  local_students, incoming_students = data_handler.convert_categories_to_numerical(local_students, incoming_students, hobbies)

  #adjust dates
  current_date = datetime.now()
  data_handler.adjust_dataframe_dates(local_students, ['Availability', 'AvailabilityText'], current_date)
  data_handler.adjust_dataframe_dates(incoming_students, ['Arrival'], current_date)

  # calulate capacities of the local students and number of  incoming students
  base_local_capacity: int  = data_handler.get_base_capacities(local_students)
  base_incoming_necessity: int = data_handler.get_base_necessity(incoming_students)

  print(f"Base local capacity: {base_local_capacity}")
  print(f"Base incoming: {base_incoming_necessity}")


  # compute the bounds for the different categories
  config = configparser.ConfigParser()
  config.read("config/config.ini")
  normal_dict: Dict[str, Union[float,int]] = normalization_calculator.compute_normalization_values(
    local_students, incoming_students, config, hobbies, faculty_distances)

  print(normal_dict)

if __name__ == '__main__':
  main()
