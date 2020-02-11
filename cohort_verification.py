#!/usr/bin/env python
# coding: utf-8

# # Uniqname Error Finder for Student Explorer application
# In [Student Explorer](https://github.com/tl-its-umich-edu/student_explorer/), if a cohort is created with a student uniqname that doesn't match to a student in edwprod.world CNLYR002 DM_STDNT table, the way this manifests in the application is that the advisor sees a student in their "My Students" view named "Not Happened Yet".
#
# DM_STDNT contains any student who has taken a course at the University of Michigan-Ann Arbor that uses Canvas. This generally includes all undergraduate and graduate students enrolled in residential programs and some students enrolled in online programs (if the program uses Canvas; some don't).
#
# This program was created in order to figure out which cohorts have "bad" student uniqname values and which values are causing the error.
#
# The intention is that you will go to the advisor to let them know about the error so that they can decide whether or not to fix it. Detailed below are some common reasons that the uniqname causes an error and the fix.
# <table>
#     <tr>
#         <th>Reason</th>
#         <th>Fix</th>
#     </tr>
#     <tr>
#         <td>
#             The uniqname contains a typo
#         </td>
#         <td>
#             Get the correct uniqname from the advisor
#         </td>
#     </tr>
#     <tr>
#         <td>
#             The student ended up not enrolling at U-M
#         </td>
#         <td>
#             Remove, if the student will never enroll
#         </td>
#     </tr>
#     <tr>
#         <td>
#             The student delayed their start term
#         </td>
#         <td>
#             Keep, if student will eventually enroll
#         </td>
#     </tr>
#     <tr>
#         <td>
#             The student is a PhD candidate no longer taking classes
#         </td>
#         <td>
#             Remove, if the student will not take any more classes
#         </td>
#     </tr>
# </table>

# ## Running this program
#
# ### .py vs .ipynb
#
# Files are provided in both .py (Python program) and .ipynb (Jupyter Notebook) format. You can choose which to use. The program was written in a Jupyter Notebook and then exported to Python, so the comments in the Python program are more difficult to read. I recommend running the program in the Jupyter Notebook the first time and running it step by step so that you can become familiar with what the program is doing, but after the first time it may be more convenient to use the Python program.
#
# ### Prerequisites
#
# 1. You must have the read-only credentials (username and password) to the Student Explorer production MySQL database.
#
# 1. You must have your own read-only credentials (username and password) for the U-M Enterprise Data Warehouse edwprod.world that provide you access to (at minimum) CNLYR002 tables BG_STDNT_CHRT_MNTR, DM_CHRT, and DM_STDNT.
#
# ### Initial setup (first time only)
#
# 1. Clone this repo to your computer by navigating to the directory/folder where you want it and entering `git clone https://github.com/mfldavidson/student_explorer_uniqname_error_finder.git` in your command line.
#
# 1. Create a virtual environment (`python3 -m venv whateveryouwanttonameit`) wherever you keep your virtual environments.
#
# 1. Activate the virtual environment (`source whateveryounamedthevirtualenv/bin/activate` if you are on a Mac, or `source whateveryounamedthevirtualenv/Scripts/activate` if you are on a PC).
#
# 1. Install all necessary libraries by navigating to the repo and then running the command `pip install -r requirements.txt`
#
# 1. Create a file named `db_creds.py` and enter the following code in it, replacing the word 'REPLACE' with the appropriate credentials.
#
# ```
# # Your own Oracle edwprod.world read-only credentials
# oracreds = {
#     'user' : 'REPLACE',
#     'password' : 'REPLACE'
# }
#
# # Student Explorer production MySQL read-only credentials
# mysqlcreds = {
#     'user': 'REPLACE',
#     'password': 'REPLACE'
# }
#
# ```
#
# ### Directions for running the program after setup
#
# 1. Activate the virtual environment (`source whateveryounamedthevirtualenv/bin/activate` if you are on a Mac, or `source whateveryounamedthevirtualenv/Scripts/activate` if you are on a PC).
#
# 1. Connect to the [U-M VPN](https://its.umich.edu/enterprise/wifi-networks/vpn).
#
# 1. Navigate in the command line to the directory where these files are located on your computer.
#
# 1. There are different instructions for using the .ipynb method vs .py:
# - If you are choosing to run the Jupyter Notebook: run the command `jupyter notebook` in your command line, then open the Jupyter Notebook in the browser window that opens. You may opt to run the Notebook line by line or all at once; it's up to you.
# - If you are choosing to run the Python program: run the command `python cohort_verification.py` in your command line.
#
# 1. The program should create a CSV named `uniqname_errors.csv` that outputs, for every cohort in Student Explorer that has a bad student uniqname value, the value that caused the error, the affected cohort, and the advisor to whom the student was mapped. This way, you can go to that advisor to address the issue. Note that the same student may appear multiple times if they are in multiple cohorts or have multiple advisors assigned to them.

# In[1]:


import pymysql # For connecting to the Student Explorer MySQL database
import cx_Oracle # For connecting to the edwprod.world Oracle database
import pandas as pd
import numpy as np
from db_creds import * # Get the database credentials stored in db_creds.py


# ### Get the cohorts with bad data
# We can find out which cohorts have "bad" data in them (i.e. a uniqname for a student who didn't match a student in edwprod.world CNLYR002.DM_STDNT) by querying edwprod.world. We will then use this list of cohorts to find the "bad" data in each cohort.

# In[3]:


# Set up the connection to edwprod.world using credentials stored in db_creds.py
# Make sure to not put your username, password, or tns data in this file!
conora = cx_Oracle.connect(user=oracreds['user'], password=oracreds['password'], dsn=dsn_tns)


# In[4]:


# Create a SQL string to get our cohorts with bad data
query_cohorts = ('SELECT DISTINCT '
                    'COHORT.CHRT_KEY "Cohort Key", '
                    'COHORT.CHRT_CD "Cohort Code", '
                    'COHORT.CHRT_DES "Cohort Name" '
                'FROM CNLYR002.BG_STDNT_CHRT_MNTR BRIDGE '
                'LEFT JOIN CNLYR002.DM_CHRT COHORT ON COHORT.CHRT_KEY = BRIDGE.CHRT_KEY '
                'WHERE BRIDGE.STDNT_KEY < 0 '
                'ORDER BY COHORT.CHRT_CD')


# In[5]:


# Run the SQL query and load the data into a data frame
bad_cohorts = pd.read_sql(query_cohorts, conora)
bad_cohorts.head()


# ### Get the processed cohort data
# We can access the list of student-advisors mappings that were successfully processed using the edwprod.world database. We will then load that data into a dataframe named valid_cohort.

# In[6]:


# Create a string of all cohorts to query for
cohort_str_key = bad_cohorts.astype({'Cohort Key':'str'})['Cohort Key'].str.cat(sep=", ")
cohort_str_key = "({})".format(cohort_str_key)
cohort_str_key


# In[7]:


# Construct the query with our cohort_str
query_valid = ('SELECT DISTINCT STU.STDNT_UM_UNQNM "Student", '
                'BRIDGE.CHRT_KEY "Cohort Key" '
                'FROM CNLYR002.BG_STDNT_CHRT_MNTR BRIDGE '
                'LEFT JOIN CNLYR002.DM_STDNT STU ON STU.STDNT_KEY = BRIDGE.STDNT_KEY '
                f'WHERE BRIDGE.CHRT_KEY IN {cohort_str_key} '
                'AND BRIDGE.STDNT_KEY > 0')


# In[8]:


# Run the query and load it into a data frame
valid_stus = pd.read_sql(query_valid, conora)
valid_stus.head()


# In[9]:


# Convert our uniqnames to lowercase to match the raw data
valid_stus.Student = valid_stus.Student.str.lower()
valid_stus.head()


# In[10]:


conora.close()


# ### Get the raw cohort data
# We can access the list of student-advisor mappings that were provided to us by the advisor and uploaded in Student Explorer management using the MySQL database. We will then load that data into a dataframe named raw_cohort.

# In[11]:


# Set up the connection
conmysql = pymysql.connect(host='tl-prod-mysql.aws.vdc.it.umich.edu',
                      port=3306,
                      user=mysqlcreds['user'],
                      password=mysqlcreds['password'],
                      database='student_explorer',
                      cursorclass=pymysql.cursors.Cursor)


# In[12]:


# Create a string of the cohort codes to use in the query like we did with key
cohort_str_code = bad_cohorts['Cohort Code'].str.cat(sep="', '")
cohort_str_code = "('{}')".format(cohort_str_code)
cohort_str_code


# In[13]:


# Create a SQL string to get raw data for the bad cohorts
query_raw = ('SELECT student_id "Student", '
             'mentor_id "Advisor", '
             'cohort_id "Cohort Code"'
             'FROM management_studentcohortmentor '
             f'''WHERE cohort_id IN {cohort_str_code};''')


# In[14]:


raw_cohort = pd.read_sql(query_raw, conmysql)


# In[15]:


raw_cohort.head()


# In[16]:


conmysql.close()


# ### Join the data frames
# We now have a data frame of students who we know are valid, and the raw input of students. We want to join them so we can see which students are in the raw input but not in the list of valid students. Those are our "bad" students. We need to also join the bad cohort data frame because it contains the "bridge" between the cohort information in the two.

# In[17]:


# Merge valid_stus and bad_cohorts so we have the cohort code to go with valid_stus
valid_cohorts = valid_stus.merge(bad_cohorts, on='Cohort Key', how='outer')
valid_cohorts.head()


# In[18]:


# Merge valid_cohorts with raw_cohorts now that we can use the Cohort Code in both
merged = valid_cohorts.merge(raw_cohort, how='outer', on=['Student','Cohort Code'])
merged.head()


# In[19]:


# Create a data frame filtered from merged where Cohort Name is null
# If Cohort Name is null then we know they weren't in valid_stus
bad_stus = merged[ merged['Cohort Name'].isnull()].copy()
bad_stus


# In[20]:


# Drop unnecessary columns since we know they contain null data
bad_stus.drop(['Cohort Key', 'Cohort Name'], axis=1, inplace=True)


# In[21]:


# Merge the cohort dataframe in so we have the name of the cohort
# This allows us to use the name when communicating with the advisor
final = bad_stus.merge(bad_cohorts, on='Cohort Code', how='left')
final


# ### Create a CSV File
# Create a CSV file with the "bad students," the cohort, and advisor.

# In[22]:


# Add a column for the advisor's email for your convenience in emailing them
final['Advisor Email'] = final.Advisor.apply(lambda x: x+'@umich.edu')


# In[23]:


# Write to CSV
final.to_csv('uniqname_errors.csv', index=False, columns=['Student', 'Advisor', 'Advisor Email', 'Cohort Name'])


# In[ ]:
