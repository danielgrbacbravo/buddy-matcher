import pandas as pd
import colorlog as logging

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
                "local_student_fullname": local_students.loc[i]["FirstName"] + " " + local_students.loc[i]["LastName"],
                "local_student_age": local_students.loc[i]["Age"],
                "local_student_gender": local_students.loc[i]["Gender"],
                "local_student_country": local_students.loc[i]["Country"],
                "incoming_student_fullname": incoming_students.loc[incoming_student_index]["FirstName"] + " " + incoming_students.loc[incoming_student_index]["LastName"],
                "incoming_student_age": incoming_students.loc[incoming_student_index]["Age"],
                "incoming_student_gender": incoming_students.loc[incoming_student_index]["Gender"],
                "incoming_student_email": incoming_students.loc[incoming_student_index]["Email"],
                "incoming_student_country": incoming_students.loc[incoming_student_index]["Country"],
                "distance": distance
            })

    output = pd.DataFrame(output_data)

    sorted_output = output.sort_values(by=["local_student_fullname", "distance"], ascending=[True, True])

    return sorted_output

def save_report(output: pd.DataFrame, output_file: str) -> None:
    """
    Save the report to a file
    """
    output.to_csv(output_file, index=False)
    logging.info("Report saved to %s", output_file)




def create_report(
    matching_matrix: pd.DataFrame,
    distance_matrix: pd.DataFrame,
    local_students: pd.DataFrame,
    incoming_students: pd.DataFrame,
    file_name: str
    ) -> None:
    """
    Create a report from the matching matrix
    """

    output = convert_matching_matrix_to_output(matching_matrix, distance_matrix, local_students, incoming_students)

    save_report(output, file_name)
