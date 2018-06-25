
# coding: utf-8

# In[1]:

""" Add column for arid, lowwateruse and aridandlowwateruse for each subbasin. 
-------------------------------------------------------------------------------

This script has been edited on 20180625 to take into account the newly
columns based on stats such as moving averga and ols.


Author: Rutger Hofste
Date: 20180604
Kernel: python35
Docker: rutgerhofste/gisdocker:ubuntu16.04

Args:
    TESTING (Boolean) : Toggle testing case.
    SCRIPT_NAME (string) : Script name.
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
OVERWRITE_OUTPUT = 1
SCRIPT_NAME = 'Y2018M06D04_RH_Arid_LowWaterUse_PostGIS_30sPfaf06_V02'
OUTPUT_VERSION = 4

THRESHOLD_ARID_YEAR = 0.03 #units are m/year, threshold defined by Aqueduct 2.1
THRESHOLD_LOW_WATER_USE_YEAR = 0.012 #units are m/year, threshold defined by Aqueduct 2.1 Withdrawal

DATABASE_ENDPOINT = "aqueduct30v05.cgpnumwmfcqc.eu-central-1.rds.amazonaws.com"
DATABASE_NAME = "database01"

INPUT_TABLE_NAME = "y2018m06d25_rh_cap_linear_trends_postgis_30spfaf06_v01_v01"
OUTPUT_TABLE_NAME = SCRIPT_NAME.lower() + "_v{:02.0f}".format(OUTPUT_VERSION)

print("Input Table: " , INPUT_TABLE_NAME, 
      "\nOutput Table: " , OUTPUT_TABLE_NAME)


# In[2]:

import time, datetime, sys
dateString = time.strftime("Y%YM%mD%d")
timeString = time.strftime("UTC %H:%M")
start = datetime.datetime.now()
print(dateString,timeString)
sys.version


# In[3]:

# imports
import re
import os
import numpy as np
import pandas as pd
import aqueduct3
from datetime import timedelta
from sqlalchemy import *
pd.set_option('display.max_columns', 500)


# In[4]:

F = open("/.password","r")
password = F.read().splitlines()[0]
F.close()

engine = create_engine("postgresql://rutgerhofste:{}@{}:5432/{}".format(password,DATABASE_ENDPOINT,DATABASE_NAME))
connection = engine.connect()

sqls = []

if OVERWRITE_OUTPUT:
    sqls.append("DROP TABLE IF EXISTS {};".format(OUTPUT_TABLE_NAME))


# In[5]:

if TESTING:
    sqls.append("CREATE TABLE {} AS SELECT * FROM {} WHERE pfafid_30spfaf06 < 130000 ;".format(OUTPUT_TABLE_NAME,INPUT_TABLE_NAME))
else:
    sqls.append("CREATE TABLE {} AS SELECT * FROM {};".format(OUTPUT_TABLE_NAME,INPUT_TABLE_NAME))


# In[6]:

sqls.append("ALTER TABLE {} ADD COLUMN arid_boolean_30spfaf06 integer DEFAULT 0".format(OUTPUT_TABLE_NAME))
sqls.append("ALTER TABLE {} ADD COLUMN lowwateruse_boolean_30spfaf06 integer DEFAULT 0".format(OUTPUT_TABLE_NAME))
sqls.append("ALTER TABLE {} ADD COLUMN aridandlowwateruse_boolean_30spfaf06 integer DEFAULT 0".format(OUTPUT_TABLE_NAME))


# In[7]:

threshold_arid_month = THRESHOLD_ARID_YEAR / 12
threshold_low_water_use_month = THRESHOLD_LOW_WATER_USE_YEAR / 12


# In[8]:

# Set Arid for monthly columns
sqls.append("UPDATE {}     SET arid_boolean_30spfaf06 = 1     WHERE temporal_resolution = 'month' AND ma10_riverdischarge_m_30spfaf06 < {};".format(OUTPUT_TABLE_NAME,threshold_arid_month))


# In[9]:

# Set Arid for year columns
sqls.append("UPDATE {}     SET arid_boolean_30spfaf06 = 1     WHERE temporal_resolution = 'year' AND ma10_riverdischarge_m_30spfaf06 < {};".format(OUTPUT_TABLE_NAME,THRESHOLD_ARID_YEAR))


# In[10]:

# Set lowwateruse for monthly columns
sqls.append("UPDATE {}     SET lowwateruse_boolean_30spfaf06 = 1     WHERE temporal_resolution = 'month' AND ma10_ptotww_m_30spfaf06 < {};".format(OUTPUT_TABLE_NAME,threshold_low_water_use_month))


# In[11]:

# Set lowwateruse for year columns
sqls.append("UPDATE {}     SET lowwateruse_boolean_30spfaf06 = 1     WHERE temporal_resolution = 'year' AND ma10_ptotww_m_30spfaf06 < {};".format(OUTPUT_TABLE_NAME,THRESHOLD_LOW_WATER_USE_YEAR))


# In[12]:

# Set aridandlowwateruse
sqls.append("UPDATE {}     SET aridandlowwateruse_boolean_30spfaf06 = 1     WHERE lowwateruse_boolean_30spfaf06 =1 AND arid_boolean_30spfaf06 = 1;".format(OUTPUT_TABLE_NAME))


# In[13]:

print(len(sqls))


# In[14]:

for sql in sqls:
    print(sql)
    result = engine.execute(sql)    


# In[15]:

end = datetime.datetime.now()
elapsed = end - start
print(elapsed)


# Previous runs:  
# 0:09:22.668061  
# 0:09:36.313159  
# 0:10:52.997894
# 
# 
# 
# 

# In[16]:

engine.dispose()


# In[ ]:



