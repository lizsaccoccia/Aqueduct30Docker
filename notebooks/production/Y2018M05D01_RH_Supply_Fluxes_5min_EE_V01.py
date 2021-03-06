
# coding: utf-8

# In[1]:

""" Supply data is available in m3second and millionm3. Convert to flux.
-------------------------------------------------------------------------------
PCRGLOBWB Data for supply is provided in fluxes with units m3second. A 
previous script converted the supply data to volumes (millionm3)
(implicit per pixel/per time step); converting to fluxes (m) and storing to 
earth engine asset. 

Author: Rutger Hofste
Date: 20180501
Kernel: python35
Docker: rutgerhofste/gisdocker:ubuntu16.04

Args:

    SCRIPT_NAME (string) : Script name
    EE_VERSION (integer) : Earth Engine path version.
    INPUT_VERSION (integer) : Input version.
    OUTPUT_VERSION (integer) : Output version.
    TESTING (boolean) : Testing.

Returns:

"""

SCRIPT_NAME = "Y2018M05D01_RH_Supply_Fluxes_5min_EE_V01"
EE_VERSION = 9
INPUT_VERSION = 1
OUTPUT_VERSION = 1 
TESTING = 0

ee_path = "projects/WRI-Aquaduct/PCRGlobWB20V{:02.0f}".format(EE_VERSION)

print("Input ee: " + ee_path +
      "\nOutput ee: " + ee_path )


# In[2]:

import time, datetime, sys
dateString = time.strftime("Y%YM%mD%d")
timeString = time.strftime("UTC %H:%M")
start = datetime.datetime.now()
print(dateString,timeString)
sys.version


# In[3]:

import subprocess
import pandas as pd
import ee
import re
from retrying import retry
from datetime import timedelta
import aqueduct3

ee.Initialize()


# In[4]:

def update_property_script_used(image):
    image = image.set("script_used",SCRIPT_NAME)
    return image

def update_property_output_version(image):
    image = image.set("output_version",OUTPUT_VERSION)
    return image

def ic_volume_to_flux_5min_millionm3_m2(ic_input_asset_id,output_version):
    """ Convert an imagecollection from volume to flux.
    -------------------------------------------------------------------------------
    The result is stored in an imagecollection with the same name as the input
    imagecollection but with 'm' instead of 'millionm3'.
    
    Input ic:
    global_historical_PDomWW_year_millionm3_5min_1960_2014
    
    Output ic:    
    global_historical_PDomWW_year_m_5min_1960_2014
    
    Args:
        ic_input_asset_id (string) : asset id of input imagecollection.

    """
    start_time = time.time()
    df_errors = pd.DataFrame()
    
    df = aqueduct3.earthengine.get_df_from_ic(ic_input_asset_id)
    df = aqueduct3.earthengine.add_export_parameters_for_export(df,old_unit,new_unit,output_version)
    
    # Creating ImageCollection(s)
    output_ic_asset_ids = list(df["output_ic_asset_id"].unique())
    for output_ic_asset_id in output_ic_asset_ids:
        command, result = aqueduct3.earthengine.create_imageCollection(output_ic_asset_id)
        print(command,result)
    
    
    # Bacth Converting and uploading.     
    for index, row in df.iterrows():
        elapsed_time = time.time() - start_time 
        print("Index: {:04.0f} Elapsed: {}".format(index, timedelta(seconds=elapsed_time)))
    
        description = row["description"]
        output_image_asset_id = row["output_image_asset_id"]
    
    
        if aqueduct3.earthengine.asset_exists(output_image_asset_id):
            print("Asset exists, skipping: {}".format(output_image_asset_id))
        else:
            i_volume_millionm3_5min = ee.Image(row["input_image_asset_id"])
            i_flux_m_5min = aqueduct3.earthengine.volume_to_flux_5min_millionm3_m2(i_volume_millionm3_5min)
            i_flux_m_5min = update_property_script_used(i_flux_m_5min)
            i_flux_m_5min = update_property_output_version(i_flux_m_5min)
            

            aqueduct3.earthengine.export_image_global_5min(i_flux_m_5min,description,output_image_asset_id)
            print(output_image_asset_id)    
    
    return df


# In[5]:

old_unit = "millionm3"
new_unit = "m"

temporal_resolutions = ["year","month"]
indicators = ["riverdischarge"]

if TESTING:
    temporal_resolutions = ["year"]
    
df = pd.DataFrame()
for indicator in indicators:
    for temporal_resolution in temporal_resolutions:
        print(indicator,temporal_resolution)
        ic_input_file_name = "global_historical_{}_{}_millionm3_5min_1960_2014".format(indicator,temporal_resolution)
        ic_input_asset_id = "{}/{}".format(ee_path,ic_input_file_name)
        df = ic_volume_to_flux_5min_millionm3_m2(ic_input_asset_id,OUTPUT_VERSION)    
    


# In[6]:

df.head()


# In[7]:

end = datetime.datetime.now()
elapsed = end - start
print(elapsed)


# Previous runs:  
# 0:42:49.746473

# In[ ]:



