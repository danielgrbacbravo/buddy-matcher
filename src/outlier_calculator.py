import pandas as pd
import numpy as np
from typing import Union, Optional
import colorlog
import logging

def calculate_outliers(data: pd.DataFrame, threshold: float = 2.0, std: float = 1.0) -> pd.Series:
    """Calculates outliers in a series of data using the z-score method.

    Args:
        age_data (pd.Series): Series of numerical data (e.g., ages).
        threshold (float): Threshold for determining outliers. Defaults to 2.0.
        std_data (Optional[pd.Series]): Series of standard deviation data. If None, calculate from age_data.

    Returns:
        pd.Series: Boolean series indicating whether each data point is an outlier.
    """
    # Extract age data from the DataFrame
    age_data: pd.Series = pd.Series(data['Age'].values)
    mean_data = age_data.mean()
    z_scores = (age_data - mean_data) / std
    outliers: pd.Series = (z_scores < -threshold) | (z_scores > threshold)

    return outliers

def remove_outliers(data: pd.DataFrame, outliers: pd.Series | np.ndarray) -> pd.DataFrame:
    # Convert Series to ndarray if necessary
    if isinstance(outliers, pd.Series):
        outliers = outliers.to_numpy()

    # Ensure that 'outliers' is a boolean mask of the same length as the data
    if len(outliers) != len(data):
        raise ValueError("Length of 'outliers' must match the number of rows in 'data'.")

    # Use 'loc' to ensure the result is a DataFrame
    return data.loc[~outliers]



def outliers_to_str(data: pd.DataFrame, outliers: pd.Series) -> list[str]:
    """returns array of strings of the names of outliers"""
    outlier_names: list[str] = []

    for index, value in outliers.items():
        if value:
            first_name = data.iloc[index]['FirstName']
            last_name = data.iloc[index]['LastName']
            age = data.iloc[index]['Age']
            outlier_names.append(f"{first_name} {last_name}  ({age} years)")

    return outlier_names
