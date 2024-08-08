# ESN Buddy Matcher

## Introduction

This project is a student pair-matching system aimed at matching local students with incoming international students based on their common interests, courses, and faculties. This can be used by higher institutions for an effective buddy system where international students are paired with a local student of the same interest.

## Installation and Run Script

in a mac or linux terminal run:

```bash
./run.sh
```

this script attempts to install all the required dependencies and libaries and set up the python virtual environment. once completed it will run the python program however it requires the correct input files to function, please read "how to use" for further instruction

## Manual Installation and Setup

1. Ensure you have `python3` installed on your system. If not, you can download and install python from [here](https://www.python.org/downloads/).

2. Clone the project to your local system. You can clone using the command below:
```git
git clone <Repository-URL>
cd path-to-folder
```
3. Set up the virtual environment. If not typically installed, you can install by running the command:
```bash
python3 -m venv .venv
```
4. Enter the following command to activate the environment:
    - On MacOS/Linux:
    ```bash
    source .venv/bin/activate
    ```
5. Install the required dependencies:
```pip
pip install -r requirements.txt
```


## How to Use

1. Once the above steps are done, run the bash shell script `run_script.sh` on your terminal. This script will install necessary dependencies and execute the main Python script. Use the command:
```bash
./run.sh
```
2. The script will process the data from incoming and local students from the `input` folder. It will use hobbies from the `config/hobbies.csv` and faculty distances from `config/faculty_distances.xlsx`.

3. All results will be output to the `output` folder. If outliers are detected, two separate reports will be generated: a buddy pair report ignoring outliers, and one including outliers. If there are no outliers, only one report is generated.

## Input details

- The `input/local_students.csv` and `input/incoming_students.csv` files contain the information about the local and incoming students, respectively. The columns in these files are self-explanatory and contain relevant information needed for the match-making process.

- The hobbies are read from `config/hobbies.csv` and it's a simple list of hobbies.

- The `config/faculty_distances.xlsx` file contains distances between faculties at the school setting. This information helps delivering a more refined match-making results.

- The `config/local_students_column_renames.csv` and `config/incoming_students_column_renames.csv` help map the input column names to a standard form, facilitating data processing.

## Output details

- Output files are saved in the `output` directory.

- If outliers are detected, two separate reports will be generated. One is a 'matching_report_no_outliers.csv', which contains a buddy pair report ignoring outliers, the other 'matching_report_with_outliers.csv' will include outliers. Each row in this file represents a buddy pair, with relevant matching information included.

- If there are no outliers, only a single report 'matching_report.csv' is generated.

Please note, each time the script is run, a new output file is created with the timestamp in the filename to avoid overwriting previous results. Please make sure to review the latest file for the most recent results.

---

That's it! You've now successfully setup and run the ESN Buddy Matcher.
