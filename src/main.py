#!/usr/bin/env python3

# Importing external libraries
from datetime import datetime
from typing import Dict
import pandas as pd
import os

# Importing internal libraries
import data_handler

def main():
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
  incoming_students: pd.DataFrame = pd.read_csv("input/incoming_students.csv")


  # clean and filter the data
  local_students, incoming_students = data_handler.clean_data(local_students, incoming_students)
  local_students, incoming_students = data_handler.rename_timestamps(local_students, incoming_students)
  local_students, incoming_students, removed_local_students, removed_incoming_students = data_handler.apply_filters(local_students, incoming_students)


  # clean dataframes
  local_students, incoming_students = data_handler.generate_cleaned_dataframes(local_students, incoming_students, None,None,None)


  # Remap the columns in the dataframes for consistency
  column_mapping: Dict[str, str] = data_handler.read_column_mapping("config/local_students_column_renames.csv")
  local_students = data_handler.remap_columns(column_mapping,local_students)

  column_mapping = data_handler.read_column_mapping("config/incoming_students_column_renames.csv")
  incoming_students = data_handler.remap_columns(column_mapping,incoming_students)


  # convert categories to numerical values
  local_students, incoming_students = data_handler.convert_categories_to_numerical(local_students, incoming_students,"config/hobbies.csv")

  #adjust dates
  current_date = datetime.now()
  data_handler.adjust_dataframe_dates(local_students, ['Availability', 'AvailabilityText'], current_date)
  data_handler.adjust_dataframe_dates(incoming_students, ['Arrival'], current_date)

  # calulate capacities of the local students and number of  incoming students
  base_local_capacity: int  = data_handler.get_base_capacities(local_students)
  base_incoming_necessity: int = data_handler.get_base_necessity(incoming_students)

  print(f"Base local capacity: {base_local_capacity}")
  print(f"Base incoming: {base_incoming_necessity}")

if __name__ == '__main__':
  main()