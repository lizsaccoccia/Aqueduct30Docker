
# coding: utf-8

# In[1]:

""" Store sample demand and riverdischarge geotiffs in S3 folder. 
-------------------------------------------------------------------------------

Author: Rutger Hofste
Date: 20180604
Kernel: python35
Docker: rutgerhofste/gisdocker:ubuntu16.04

"""

SCRIPT_NAME = "Y2018M06D04_RH_QA_download_sample_geotiffs_5min_V01"
OUTPUT_VERSION = 2

S3_INPUT_PATH =  "s3://wri-projects/Aqueduct30/processData/Y2017M07D31_RH_Convert_NetCDF_Geotiff_V02/output_V02/"
s3_output_path = "s3://wri-projects/Aqueduct30/qaData/{}/output_V{:02.0f}/".format(SCRIPT_NAME,OUTPUT_VERSION)

print("\nInput S3: " + S3_INPUT_PATH +
      "\nOutput S3: " +  s3_output_path)


# In[2]:

indicator = "*" #options: ["riverdischarge","PDomWW, "*" wildcard]
temporal_resolution = "month"
unit = "*" # option:  ["m3second" or "milliom3" to limit to supply or demand.]
year = 2010
month =  4


# In[3]:

import re
import os


# In[4]:

filename = "global_historical_{}_{}_{}_5min_1960_2014_I*Y{:04.0f}M{:02.0f}.tif".format(indicator,temporal_resolution,unit,year,month)


# In[5]:

filename


# In[6]:

get_ipython().system('aws s3 cp {S3_INPUT_PATH} {s3_output_path} --recursive --exclude "*" --include {filename}')


# https://code.earthengine.google.com/6da1c9ab09c4296ebf814ca720cfee54

# In[ ]:



