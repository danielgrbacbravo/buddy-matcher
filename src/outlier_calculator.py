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
    colorlog.debug("calculating outliers")
    # Extract age data from the DataFrame
    age_data: pd.Series = pd.Series(data['Age'].values)
    mean_data = age_data.mean()
    z_scores = (age_data - mean_data) / std
    outliers = (z_scores < -threshold) | (z_scores > threshold)

    return outliers

def outliers_to_str(data: pd.DataFrame, outliers: pd.Series) -> list[str]:
    """returns array of strings of the names of outliers"""
    outliars = []
    for index, value in outliers.items():
        if value:
            outliars.append(data['FirstName'][index] + " " + data['LastName'][index])
    return outliars
