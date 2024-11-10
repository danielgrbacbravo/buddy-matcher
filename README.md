# ESN Buddy Matcher

## Introduction

This project is a student pair-matching system aimed at matching local students with incoming international students based on their common interests, courses, and faculties. This can be used by higher institutions for an effective buddy system where international students are paired with a local student of the same interest.






## Usage
the best way to use this project is though a docker container as it will ensure that all dependencies are installed and the script is run in a controlled environment. To use the docker container, follow the steps below:

1. Create a directory on your local machine where you want to store the project files. You can do this by running the command below:
```bash
mkdir esn-buddy-matcher
cd esn-buddy-matcher
```

2. Create a docker-compose.yml file in the directory you created above. You can do this by running the command below:
```bash
touch docker-compose.yml
```

3. Open the docker-compose.yml file in a text editor and add the following content:
```yaml
services:
  buddy-matcher:
    image: daiigr/buddy-matcher:latest
    container_name: buddy-matcher
    volumes:
      - ./config:/config
      - ./input:/input
      - ./output:/output
```

4. run the following command to start the docker container:
```bash
docker compose up
```

5. the first time you run the container, the necessary directories will be created in the `config`, `input`, and `output` directories. You can then add the necessary files to the `input` and `config` directories
once the files are added, you can start the docker container again by running the command below:
```bash
docker compose up
```



















## Installation and Run Script


1. Clone the project to your local system. You can clone using the command below:
```git
git clone <Repository-URL>
cd path-to-folder
```
2. Run the bash shell script `run.sh` on your terminal. This script will install necessary dependencies and execute the main Python script. Use the command:
```bash
./run.sh
```

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

1. Once the above steps are done, run the bash shell script `run.sh` on your terminal. This script will install necessary dependencies and execute the main Python script. Use the command:
```bash
./run.sh
```

2. if you prefer to run the script manually, you can run the following command:
```bash
python3 src/main.py
```

2. The script will process the data from incoming and local students from the `input` folder. It will use hobbies from the `config/hobbies.csv` and faculty distances from `config/faculty_distances.xlsx`.

3. All results will be output to the `output` folder. If outliers are detected, two separate reports will be generated: a buddy pair report ignoring outliers, and one including outliers. If there are no outliers, only one report is generated.

## Input details

- The `input/local_students.csv` and `input/incoming_students.csv` files contain the information about the local and incoming students, respectively. The columns in these files are self-explanatory and contain relevant information needed for the match-making process.

- The hobbies are read from `config/hobbies.csv` and it's a simple list of hobbies.

- The `config/faculty_distances.xlsx` file contains distances between faculties at the school setting. This information helps delivering a more refined match-making results.

- The `config/local_students_column_renames.csv` and `config/incoming_students_column_renames.csv` help map the input column names to a standard form, facilitating data processing. practically speaking, they map one set of header names to another so that they match for processing

## Output details

- Output files are saved in the `output` directory.

- If outliers are detected, two separate reports will be generated. One is a 'matching_report_no_outliers.csv', which contains a buddy pair report ignoring outliers, the other 'matching_report_with_outliers.csv' will include outliers. Each row in this file represents a buddy pair, with relevant matching information included.

- If there are no outliers, only a single report 'matching_report.csv' is generated.

Please note, each time the script is run, a new output file is created with the timestamp in the filename to avoid overwriting previous results. Please make sure to review the latest file for the most recent results.

---

That's it! You've now successfully setup and run the ESN Buddy Matcher.
