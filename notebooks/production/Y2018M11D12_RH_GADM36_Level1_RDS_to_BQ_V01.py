
# coding: utf-8

# In[1]:

""" Upload GADM 3.6 level 1 to bigquery.
-------------------------------------------------------------------------------

Author: Rutger Hofste
Date: 20181112
Kernel: python35
Docker: rutgerhofste/gisdocker:ubuntu16.04

"""

TESTING = 0
OVERWRITE_OUTPUT = 1
SCRIPT_NAME = 'Y2018M11D12_RH_GADM36_Level1_RDS_to_BQ_V01'
OUTPUT_VERSION = 1

BQ_PROJECT_ID = "aqueduct30"
BQ_OUTPUT_DATASET_NAME_WKT = "geospatial_wkt_v01"
BQ_OUTPUT_DATASET_NAME_GEOG = "geospatial_geog_v01"

RDS_DATABASE_ENDPOINT = "aqueduct30v05.cgpnumwmfcqc.eu-central-1.rds.amazonaws.com"
RDS_DATABASE_NAME = "database01"
RDS_INPUT_TABLE_NAME = "y2018m11d12_rh_gadm36_level1_to_rds_v01_v02"
BQ_OUTPUT_TABLE_NAME = "{}_v{:02.0f}".format(SCRIPT_NAME,OUTPUT_VERSION).lower()

print("\nRDS_DATABASE_ENDPOINT: ", RDS_DATABASE_ENDPOINT,
      "\nRDS_DATABASE_NAME: ", RDS_DATABASE_NAME,
      "\nRDS_INPUT_TABLE_NAME: ",RDS_INPUT_TABLE_NAME,
      "\nBQ_OUTPUT_DATASET_NAME_WKT: ", BQ_OUTPUT_DATASET_NAME_WKT,
      "\nBQ_OUTPUT_DATASET_NAME_GEOG: ", BQ_OUTPUT_DATASET_NAME_GEOG,
      "\nBQ_OUTPUT_TABLE_NAME: ", BQ_OUTPUT_TABLE_NAME)


# In[2]:

import time, datetime, sys
dateString = time.strftime("Y%YM%mD%d")
timeString = time.strftime("UTC %H:%M")
start = datetime.datetime.now()
print(dateString,timeString)
sys.version


# In[3]:

import os
import sqlalchemy
import pandas as pd
import geopandas as gpd
from google.cloud import bigquery

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/.google.json"
os.environ["GOOGLE_CLOUD_PROJECT"] = "aqueduct30"
client = bigquery.Client(project=BQ_PROJECT_ID)


# In[4]:

F = open("/.password","r")
password = F.read().splitlines()[0]
F.close()

engine = sqlalchemy.create_engine("postgresql://rutgerhofste:{}@{}:5432/{}".format(password,RDS_DATABASE_ENDPOINT,RDS_DATABASE_NAME))


# In[5]:

sql = """
SELECT
  gid_1,
  name_1,
  gid_0,
  name_0,
  varname_1,
  nl_name_1,
  type_1,
  engtype_1,
  cc_1,
  hasc_1,
  geom,
  ST_AsText(geom) AS wkt
FROM
  {}
""".format(RDS_INPUT_TABLE_NAME)


# In[6]:

gdf = gpd.read_postgis(sql=sql,
                       con=engine)


# In[7]:

gdf.shape


# In[8]:

gdf.head()


# In[9]:

destination_table_wkt = "{}.{}".format(BQ_OUTPUT_DATASET_NAME_WKT,BQ_OUTPUT_TABLE_NAME)


# In[10]:

df = pd.DataFrame(gdf.drop("geom",1))


# In[11]:

if TESTING:
    df = df.sample(1000)


# In[12]:

df.to_gbq(destination_table=destination_table_wkt,
          project_id=BQ_PROJECT_ID,
          chunksize=100,
          if_exists="replace")


# In[13]:

engine.dispose()


# In[14]:

job_config = bigquery.QueryJobConfig()


# In[21]:

q = """
SELECT
  gid_1,
  name_1,
  gid_0,
  name_0,
  varname_1,
  nl_name_1,
  type_1,
  engtype_1,
  cc_1,
  hasc_1,
  ST_GeogFromText(wkt) AS geog
FROM
  {}
""".format(destination_table_wkt)


# In[22]:

destination_dataset_ref = client.dataset(BQ_OUTPUT_DATASET_NAME_GEOG)


# In[23]:

destination_table_ref = destination_dataset_ref.table(BQ_OUTPUT_TABLE_NAME)


# In[24]:

job_config.destination = destination_table_ref


# In[25]:

query_job = client.query(query=q,
                         job_config=job_config)


# In[26]:

rows = query_job.result()


# In[ ]:

end = datetime.datetime.now()
elapsed = end - start
print(elapsed)


# previous runs:  
# 0:14:59.092810  
# 0:12:43.245526
# 

# In[ ]:



