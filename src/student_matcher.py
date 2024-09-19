import munkres
import pandas as pd
import numpy as np
from pandas.core.groupby.groupby import Union
import colorlog as logging
from tqdm import tqdm
from scipy.optimize import linear_sum_assignment

def compute_optimal_pairs(distance_matrix: pd.DataFrame, local_students: pd.DataFrame, incoming_students: pd.DataFrame, base_local_capacity: int, base_incoming_necessity: int) -> pd.DataFrame:
    """
    Computes the optimal pairs of local and incoming students based on a distance matrix.

    This function uses the Munkres algorithm to find the best matches between local students and incoming students
    while considering the capacity of local students and the necessity of incoming students. The function iteratively
    adjusts the matching based on the capacities of local students, ensuring that only those who can accommodate the
    current number of matches are considered.

    Parameters:
    - distance_matrix (pd.DataFrame): A DataFrame representing the distances between local and incoming students.
    - local_students (pd.DataFrame): A DataFrame containing information about local students, including their capacities.
    - incoming_students (pd.DataFrame): A DataFrame containing information about incoming students.
    - base_local_capacity (int): The base capacity limit for local students.
    - base_incoming_necessity (int): The base necessity limit for incoming students.

    Returns:
    - pd.DataFrame: A DataFrame indicating the matching between local and incoming students, where 1 indicates a match.
    """

    print(distance_matrix)
    local_students = local_students.copy()
    incoming_students = incoming_students.copy()

    matching_matrix: pd.DataFrame = pd.DataFrame(np.zeros((len(local_students), len(incoming_students))), index=local_students.index, columns=incoming_students.index)
    # Get the highest capacity local student
    highest_capacity: int = int(local_students['Capacity'].max())
    print(highest_capacity)

    # Keep track of the matched incoming students
    matched_incoming_students = set()

    for i in range(highest_capacity):
        # Remove local students who do not have enough capacity for i matches
        # TODO: issue with the indexes because of drops prior to this
        for index, row in local_students.iterrows():
            if row['Capacity'] < i:
                distance_matrix = distance_matrix.drop(index)
                # Remove them from the local students dataframe (to keep indexes in sync)
                local_students = local_students.drop(index)

        # Filter distance_matrix to exclude matched incoming students
        distance_matrix_filtered = distance_matrix.loc[:, ~distance_matrix.columns.isin(matched_incoming_students)]
        print(distance_matrix_filtered)

        # Only proceed if there are local students and incoming students to match
        if not local_students.empty and not distance_matrix_filtered.empty:
            m = munkres.Munkres()

            # Convert the filtered DataFrame to matrix format
            matrix: munkres.Matrix = distance_matrix_filtered.values.tolist()

            # Apply the algorithm to the matrix
            indexes = m.compute(matrix)

            logging.info(indexes)
            logging.info("Creating pair set %i", i)

            for row, column in indexes:
                matching_matrix.iloc[row, column] = 1
                matched_incoming_students.add(distance_matrix_filtered.columns[column])  # Add matched incoming student to the set
    return matching_matrix
