import pandas as pd
from typing import Union, Tuple
import numpy as np

def add_matches_column(df: pd.DataFrame) -> pd.DataFrame:

    df = df.copy()
    """
    Adds a new 'Matches' column to the DataFrame if it doesn't exist.

    Parameters:
    df (pd.DataFrame): The DataFrame to which the new column will be added.

    Returns:
    pd.DataFrame: The DataFrame with the new 'Matches' column if it was not present.
    """

    if 'Matches' not in df.columns:
        df['Matches'] = None  # You can initialize it with any default value you like
        print("'Matches' column added.")
    else:
        print("'Matches' column already exists.")

    return df


def add_id(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds a new 'id' column to the DataFrame if it doesn't exist.

    Parameters:
    df (pd.DataFrame): The DataFrame to which the new column will be added.

    Returns:
    pd.DataFrame: The DataFrame with the new 'id' column if it was not present.
    """

    df_copy = df.copy()
    if 'id' not in df_copy.columns:
        df_copy = df_copy.reset_index().rename(columns={'index':'id'})
        print("'id' column added.")
    else:
        print("'id' column already exists.")

    return df_copy


def adjust_capacity(df: pd.DataFrame, column: str) -> pd.DataFrame:
  """
    Adjusts the capacity of the DataFrame based on the values in the specified column.

    Parameters:
    df (pd.DataFrame): The DataFrame to adjust.
    column (str): The column containing the values to adjust the capacity.

    Returns:
    pd.DataFrame: The DataFrame with the adjusted capacity.
  """
  # Create a copy of the dataframe to avoid modifying the original
  df_copy = df.copy()

  # Duplicate rows based on the values in the specified column
  df_copy = df_copy.loc[df_copy.index.repeat(df_copy[column])]

  # Assign 1 to the specified column and 'No' to a new 'Extra' column
  df_copy = df_copy.assign(**{column: 1, 'Extra': 'No'})

  return df_copy

def handle_extra_buddies(base_local_capacity: int, base_necessity: int, local_students_copy: pd.DataFrame) -> Tuple[str, pd.DataFrame]:
    if base_local_capacity < base_necessity:
        message = "Extra Students Needed"
        additional_local_students = local_students_copy.loc[
            local_students_copy['ExtraBuddy'] == 'Yes'].assign(Capacity=0)
        local_students_copy = pd.concat([local_students_copy, additional_local_students],
                                             ignore_index=True,
                                             axis=0).sort_values('id').reset_index(drop=True)
    else:
        local_students_copy = local_students_copy.sort_values('id').reset_index(drop=True)
        message = "No Extra Students Needed"

    return message, local_students_copy


def _prepare_for_one_to_one_matching(self):
    self.add_matches_column()
    self.add_id_and_adjust_capacity()
    self.handle_extra_buddies()
