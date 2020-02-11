
# Uniqname Error Finder for Student Explorer application
In [Student Explorer](https://github.com/tl-its-umich-edu/student_explorer/), if a cohort is created with a student uniqname that doesn't match to a student in edwprod.world CNLYR002 DM_STDNT table, the way this manifests in the application is that the advisor sees a student in their "My Students" view named "Not Happened Yet".

DM_STDNT contains any student who has taken a course at the University of Michigan-Ann Arbor that uses Canvas. This generally includes all undergraduate and graduate students enrolled in residential programs and some students enrolled in online programs (if the program uses Canvas; some don't).

This program was created in order to figure out which cohorts have "bad" student uniqname values and which values are causing the error.

The intention is that you will go to the advisor to let them know about the error so that they can decide whether or not to fix it. Detailed below are some common reasons that the uniqname causes an error and the fix.
<table>
    <tr>
        <th>Reason</th>
        <th>Fix</th>
    </tr>
    <tr>
        <td>
            The uniqname contains a typo
        </td>
        <td>
            Get the correct uniqname from the advisor
        </td>
    </tr>
    <tr>
        <td>
            The student ended up not enrolling at U-M
        </td>
        <td>
            Remove, if the student will never enroll
        </td>
    </tr>
    <tr>
        <td>
            The student delayed their start term
        </td>
        <td>
            Keep, if student will eventually enroll
        </td>
    </tr>
    <tr>
        <td>
            The student is a PhD candidate no longer taking classes
        </td>
        <td>
            Remove, if the student will not take any more classes
        </td>
    </tr>
</table>

## Running this program

### .py vs .ipynb

Files are provided in both .py (Python program) and .ipynb (Jupyter Notebook) format. You can choose which to use. The program was written in a Jupyter Notebook and then exported to Python, so the comments in the Python program are more difficult to read. I recommend running the program in the Jupyter Notebook the first time and running it step by step so that you can become familiar with what the program is doing, but after the first time it may be more convenient to use the Python program.

### Prerequisites

1. You must have the read-only credentials (username and password) to the Student Explorer production MySQL database.

1. You must have your own read-only credentials (username and password) for the U-M Enterprise Data Warehouse edwprod.world that provide you access to (at minimum) CNLYR002 tables BG_STDNT_CHRT_MNTR, DM_CHRT, and DM_STDNT.

1. You must have the connection string from the tnsnames.ora file for connecting to edwprod.world (usually just a section in a larger tnsnames.ora file for all U-M enterprise data warehouses)

### Initial setup (first time only)

1. Clone this repo to your computer by navigating to the directory/folder where you want it and entering `git clone https://github.com/mfldavidson/student_explorer_uniqname_error_finder.git` in your command line.

1. Create a virtual environment (`python3 -m venv whateveryouwanttonameit`) wherever you keep your virtual environments.

1. Activate the virtual environment (`source whateveryounamedthevirtualenv/bin/activate` if you are on a Mac, or `source whateveryounamedthevirtualenv/Scripts/activate` if you are on a PC).

1. Install all necessary libraries by navigating to the repo and then running the command `pip install -r requirements.txt`

1. Create a file named `db_creds.py` and enter the following code in it, replacing the word 'REPLACE' with the appropriate credentials and string.

```
# Your own Oracle edwprod.world read-only credentials
oracreds = {
    'user' : 'REPLACE',
    'password' : 'REPLACE'
}

# Student Explorer production MySQL read-only credentials
mysqlcreds = {
    'user': 'REPLACE',
    'password': 'REPLACE'
}

# The exact string after 'edwprod.world=' from the tnsnames.ora file--should start with (DESCRIPTION=
dsn_tns = '''REPLACE'''

```

### Directions for running the program after setup

1. Activate the virtual environment (`source whateveryounamedthevirtualenv/bin/activate` if you are on a Mac, or `source whateveryounamedthevirtualenv/Scripts/activate` if you are on a PC).

1. Connect to the [U-M VPN](https://its.umich.edu/enterprise/wifi-networks/vpn).

1. Navigate in the command line to the directory where these files are located on your computer.

1. There are different instructions for using the .ipynb method vs .py:
- If you are choosing to run the Jupyter Notebook: run the command `jupyter notebook` in your command line, then open the Jupyter Notebook in the browser window that opens. You may opt to run the Notebook line by line or all at once; it's up to you.
- If you are choosing to run the Python program: run the command `python cohort_verification.py` in your command line.

The program should create a CSV named `uniqname_errors.csv` that outputs, for every cohort in Student Explorer that has a bad student uniqname value, the value that caused the error, the affected cohort, and the advisor to whom the student was mapped. This way, you can go to that advisor to address the issue. Note that the same student may appear multiple times if they are in multiple cohorts or have multiple advisors assigned to them.
