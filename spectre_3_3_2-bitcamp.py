'''
Caitlyn Singam, (c) 2017
Spectre - deanonymiser software
07 April 2017 (Bitcamp 2017)

'''

from pprint import pprint
from jsonmerge import merge
from jsonmerge import Merger
import json
import os
import string
from collections import Counter
import itertools
import requests
import numpy as np
import gmplot

#for jsonmerger. prevents it from overwriting things
schema = {
    "properties": {
        "event":{
            "mergeStrategy": "append"
         }
    }
}

        
merger = Merger(schema)
API_KEY = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
def address_resolver(json):
    final = {}
    if json['results']:
        data = json['results'][0]
        for item in data['address_components']:
            for category in item['types']:
                data[category] = {}
                data[category] = item['long_name']
        final['latitude'] = data.get("geometry", {}).get("location", {}).get("lat", None)
        final['longitude'] = data.get("geometry", {}).get("location", {}).get("lng", None)
    return final

def get_address_details(address,):
    url = 'https://maps.googleapis.com/maps/api/geocode/json?components=&language=&region=&bounds=&key=' 
    url = url + '&address='+ address.replace(" ","+")
    response = requests.get(url)
    data  = address_resolver(response.json())
    #data['address'] = address
    return data

def readJSON (filename):
    "Reads in a JSON file, like one might assume a function by this name might do."
    with open(filename) as json_data:
        file=json.load(json_data)
        return file;

list = [];
def search(values, searchFor):
    for k in values:
        if values[k].find(searchFor)!=-1:
            list.append(values[k])        
    return list

needToInitialise = 1
#takes in all .json files from the directory, merges them, and outputs a variable containing the json
for file in os.listdir("C:/Users/Admin/Documents/Spectre deanonymiser"):
    if file.endswith(".json"):
        if(needToInitialise):
            mergedFile = readJSON(file)
            needToInitialise = 0 #ensures that we are not merging with an empty file
        else:
            mergedFile = merger.merge(readJSON(file),mergedFile)

d={} #init dictionary of times/queries
for item in mergedFile["event"]:
    d.update({item['query']['id'][0]['timestamp_usec']:item['query']['query_text']});


fromPlace=[];toPlace=[];
#parse locations visited
loc = search(d,'->') #this is the format that google maps searches come up in
for entry in loc:
    hold = entry.split(' -> ')
    fromPlace.append(hold[0])
    toPlace.append(hold[1])   
fromdata=[];
todata=[];
fromLat=[];fromLong=[];
homeLat=0;homeLong=0;workLat=0;workLong=0;
for place in fromPlace:
    fromdata.append(get_address_details(place))
    fromdata = [x for x in fromdata if x]

for i in range(0,len(fromdata)-1):
    fromLat.append(fromdata[i]['latitude'])
    fromLong.append(fromdata[i]['longitude'])

homeLat = np.mean(fromLat)
homeLong = np.mean(fromLong)
fromRadius=(692/36)*np.mean([np.std(fromLat),np.std(fromLong)])
for place in toPlace:
    todata.append(get_address_details(place))
    todata = [x for x in todata if x]

toLat=[];toLong=[];
for i in range(0,len(todata)-1):
    toLat.append(todata[i]['latitude'])
    toLong.append(todata[i]['longitude'])
toRadius=(692/36)*np.mean([np.std(toLat),np.std(toLong)])
workLat = np.mean(toLat)
workLong = np.mean(toLong)
gmap1 = gmplot.GoogleMapPlotter(38.989697, -76.93776, 10)
gmap1.heatmap([homeLat],[homeLong],radius=fromRadius)
gmap1.heatmap([workLat],[workLong],radius=toRadius)
gmap1.draw("specter-map-scaled.html")
        
    

