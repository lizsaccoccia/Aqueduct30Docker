
# coding: utf-8

# In[21]:

"""
Data needs to be stored in geoJSON file format. The type should be featureCollection.

Files are quite large so will have to come up with retrying 


"""

INPUT_FILE_NAME = "/volumes/data/Y2018M08D13_RH_Process_Basisregistratie_Gewaspercelen_V01/output_V05/BRP_Gewaspercelen_2015.json"


# In[22]:

import geojson
import json
import ee

ee.Initialize()


# In[23]:

ee.__version__


# In[ ]:

command = "earthengine create folder users/rutgerhofste/Y2018M08D13_RH_Ingest_GeoJSON_Earthengine_V01"
response = subprocess.check_output(command,shell=True)
command = "earthengine create featurecollection users/rutgerhofste/Y2018M08D13_RH_Ingest_GeoJSON_Earthengine_V01/output_V01"
response = subprocess.check_output(command,shell=True)


# In[ ]:




# In[ ]:




# In[24]:

with open(INPUT_FILE_NAME, encoding="utf-8") as f:
    data = geojson.load(f)


# In[25]:

type(data)


# In[26]:

data.crs


# In[27]:

len(data["features"])


# In[18]:

def fix_datatype(properties):
    properties["GWS_GEWASCODE"] = int(properties["GWS_GEWASCODE"])
    return properties


# In[19]:

batch_size = 5
features = []
for index , feature in enumerate(data["features"]):
    properties = feature.properties
    
    new_properties = fix_datatype(properties)
    
    geometry = feature.geometry
    geoJSONfeature = geojson.Feature(geometry=geometry,
                                     properties=properties)
    features.append(ee.Feature(geoJSONfeature))    
    if index == batch_size:
        fc = ee.FeatureCollection(features)
        task = ee.batch.Export.table.toAsset(fc,
                                             description="test",
                                             assetId = "users/rutgerhofste/test/test02")
                                             
        break


# In[20]:

properties


# In[8]:

task.start()


# In[ ]:



