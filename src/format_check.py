from datetime import datetime
import pandas as pd

def determine_datetime_format(date_str: str) -> str:
    formats = ['%d-%m-%Y', '%m-%d-%Y', '%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%Y/%m/%d']
    for fmt in formats:
        try:
            datetime.strptime(date_str, fmt)
            return fmt
        except ValueError:
            pass
    return "Unknown format"

def does_age_data_exist(data: pd.DataFrame) -> bool:
  return 'Age' in data.columns
