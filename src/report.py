import pandas as pd

def convert_matching_matrix_to_output(
    matching_matrix: pd.DataFrame,
    distance_matrix: pd.DataFrame,
    local_students: pd.DataFrame,
    incoming_students: pd.DataFrame) -> pd.DataFrame:
    """
    Convert the matching matrix to the output format
    """

    output_data = []

    # iterate over the columns of the matching matrix
    for incoming_student_index in matching_matrix.columns:
        # Get the local student index with the max value for this incoming student
       for i in range(0,len(matching_matrix[incoming_student_index])):
         if matching_matrix[incoming_student_index][i] == 1:
           distance = distance_matrix.iloc[i, incoming_students.index.get_loc(incoming_student_index)]
           output_data.append({
                "local_student": local_students.loc[i]["FirstName"],
                "incoming_student": incoming_students.loc[incoming_student_index]["FirstName"],
                "distance": distance
            })

    output = pd.DataFrame(output_data)

    sorted_output = output.sort_values(by=["local_student", "distance"], ascending=[True, True])

    return sorted_output
