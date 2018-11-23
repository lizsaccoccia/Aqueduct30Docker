
# coding: utf-8

# In[1]:

""" Cleanup, add category and label for icep at hydrobasin level 6.
-------------------------------------------------------------------------------

Author: Rutger Hofste
Date: 20181122
Kernel: python35
Docker: rutgerhofste/gisdocker:ubuntu16.04

Args:
    TESTING (Boolean) : Toggle testing case.
    SCRIPT_
    NAME (string) : Script name.
    OUTPUT_VERSION (integer) : output version.
    DATABASE_ENDPOINT (string) : RDS or postGreSQL endpoint.
    DATABASE_NAME (string) : Database name.
    TABLE_NAME_AREA_30SPFAF06 (string) : Table name used for areas. Must exist
        on same database as used in rest of script.
    S3_INPUT_PATH_RIVERDISCHARGE (string) : AWS S3 input path for 
        riverdischarge.    
    S3_INPUT_PATH_DEMAND (string) : AWS S3 input path for 
        demand.     

"""

TESTING = 0
SCRIPT_NAME = "Y2018M11D22_RH_ICEP_Hybas6_Cat_Label_BQ_V01"
OUTPUT_VERSION = 1


S3_INPUT_PATH = "s3://wri-projects/Aqueduct30/processData/Y2018M11D22_RH_ICEP_Zonal_Stats_Hybas6_EE_V01/output_V01/"

BQ_PROJECT_ID = "aqueduct30"
BQ_OUTPUT_DATASET_NAME = "aqueduct30v01"
BQ_OUTPUT_TABLE_NAME = "{}_v{:02.0f}".format(SCRIPT_NAME,OUTPUT_VERSION).lower()

ec2_input_path = "/volumes/data/{}/input_V{:02.0f}".format(SCRIPT_NAME,OUTPUT_VERSION) 
ec2_output_path = "/volumes/data/{}/output_V{:02.0f}".format(SCRIPT_NAME,OUTPUT_VERSION) 


print("S3_INPUT_PATH: ",S3_INPUT_PATH,
      "\nec2_input_path: ",ec2_input_path,
      "\nBQ_OUTPUT_DATASET_NAME: ", BQ_OUTPUT_DATASET_NAME,
      "\nBQ_OUTPUT_TABLE_NAME: ",BQ_OUTPUT_TABLE_NAME
      )


# In[2]:

import time, datetime, sys
dateString = time.strftime("Y%YM%mD%d")
timeString = time.strftime("UTC %H:%M")
start = datetime.datetime.now()
print(dateString,timeString)
sys.version


# In[3]:

get_ipython().system('rm -r {ec2_input_path}')
get_ipython().system('rm -r {ec2_output_path}')
get_ipython().system('mkdir -p {ec2_input_path}')
get_ipython().system('mkdir -p {ec2_output_path}')


# In[4]:

get_ipython().system('aws s3 cp {S3_INPUT_PATH} {ec2_input_path} --recursive')


# In[5]:

import os
import pandas as pd
import numpy as np
from google.cloud import bigquery

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/.google.json"
os.environ["GOOGLE_CLOUD_PROJECT"] = "aqueduct30"
client = bigquery.Client(project=BQ_PROJECT_ID)


# In[6]:

def normalize_score(row):
    if row <= -5:
        minV, maxV, addV = icep_min, -5, 0
    elif row <= 0:
        minV, maxV, addV = -5, -1, 0
    elif row <= 1:
        minV, maxV, addV = 0, 1, 2
    elif row <= 5:
        minV, maxV, addV = 1, 5, 3
    else:
        minV, maxV, addV = 5, icep_max, 4

    # Normalize score base on class bounds
    score = (row - minV) / (maxV - minV) + addV
    # Fix scores less than 0 or great than 5
    final_score = np.where(score < 0, 0, np.where(score > 5, 5, score))
    return final_score

def category_to_label(row):
    if row < 1:
        cat = "Low (< -5)"
    elif row < 2:
        cat = "Low to medium (-5 to 0)"
    elif row < 3:
        cat = "Medium to high (0 to +1)"
    elif row < 4:
        cat = "High (+1 to +5)"
    elif row <= 5:
        cat = "Extremely High (> +5)"
    else:
        cat = "No Data"
    return cat

def label_to_category(row):
    if row == "Low (< -5)":
        cat = 0
    elif row == "Low to medium (-5 to 0)":
        cat = 1
    elif row == "Medium to high (0 to +1)":
        cat = 2
    elif row == "High (+1 to +5)":
        cat = 3
    elif row == "Extremely High (> +5)":
        cat = 4
    else:
        cat = -1
    return cat


# In[7]:

files = os.listdir(ec2_input_path)


# In[8]:

files


# In[9]:

input_file_path = "{}/df_hybas_lev06_30s.pkl".format(ec2_input_path)


# In[10]:

df = pd.read_pickle(input_file_path)


# In[11]:

df.head()


# In[12]:

df.zones = df.zones.astype(np.int64)


# In[13]:

df = df.rename(columns={"mean":"ICEP_raw",
                        "zones":"pfaf_id"})


# In[14]:

icep_min = df["ICEP_raw"].min()
icep_max = df["ICEP_raw"].max()


# In[15]:

icep_min


# In[16]:

icep_max


# In[17]:

df["ICEP_score"] = df["ICEP_raw"].apply(lambda x: normalize_score(x))


# In[18]:

df["ICEP_label"] = df["ICEP_score"].apply(lambda x: category_to_label(x))


# In[19]:

df["ICEP_cat"] = df["ICEP_label"].apply(lambda x: label_to_category(x))


# In[20]:

df = df.drop(columns=["output_version","reducer","script_used","spatial_aggregation","spatial_resolution","unit","parameter"])


# In[21]:

df.columns = df.columns.str.lower()


# In[22]:

df.head()


# In[23]:

destination_table = "{}.{}".format(BQ_OUTPUT_DATASET_NAME,BQ_OUTPUT_TABLE_NAME)


# In[24]:

df.to_gbq(destination_table=destination_table,
          project_id=BQ_PROJECT_ID,
          chunksize=10000,
          if_exists="replace")


# In[25]:

output_file_path_pkl = "{}/icep_cat_label.pkl".format(ec2_output_path)
output_file_path_csv = "{}/icep_cat_label.csv".format(ec2_output_path)
df.to_pickle(output_file_path_pkl)
df.to_csv(output_file_path_csv,encoding='utf-8')


# In[26]:

get_ipython().system('aws s3 cp  {ec2_output_path} {S3_INPUT_PATH} --recursive')


# In[27]:

end = datetime.datetime.now()
elapsed = end - start
print(elapsed)


# Previous runs:  
# 0:00:20.201732  
# 0:00:19.542761
# 

# In[ ]:



