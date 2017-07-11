

#import modules
import sys, os
import urllib
import json
import pycurl
from StringIO import StringIO
import pandas as pd
import numpy as np

#Set the output location
outFolder = '../Scratch/Beetle'

#Set the base URL for the API
baseURL='http://data.neonscience.org/api/v0/'

#Retrieve the products listing into the buff object
buff = StringIO()
c = pycurl.Curl()
c.setopt(c.URL, baseURL+'products')
c.setopt(c.WRITEDATA, buff)
c.perform()
c.close()

#Create a dictionary of objects
body = buff.getvalue()
neonProducts = json.loads(body)

#Convert to dataframe
from pandas.io.json import json_normalize
dfAll = json_normalize(neonProducts['data'])

#Isolate active beetle data 
beetleDF = dfAll.query(("productStatus == 'ACTIVE' & productName == 'Ground beetles sampled from pitfall traps'"))

#Loop through each site code and get data URLS
siteCodes = beetleDF.siteCodes.iloc[0]
for site in siteCodes:
    #Get the list of urls
    urls = site['availableDataUrls']
    
    #Loop through each URL 
    for url in urls:

        #Fix url
        idx = url.index('/',7) 
        url2 = 'http://data.neonscience.org' + url[idx:]

        #Get the repsonse as a json object and get relevant objects
        response = urllib.urlopen(url2)
        rawData= json.load(response)
        data = rawData['data']
        siteCode = data['siteCode']
        monthYear = data['month']
        files = data['files']

        #Download all csv files
        for file in files:
            fields = file['name'].split('.')

            #Skip to next url if not a csv file
            if fields[-1] <> 'csv':
                continue
            #Create the filename
            fn = "{}-{}-{}".format(monthYear,siteCode,file['name'])
            print "retrieving {}".format(fn)
            
            #Set the output filename and url
            outFN = os.path.join(outFolder,fn)
            outURL = file['url']

            #Save the CSV file
            response = urllib.urlopen(outURL)
            with open(outFN,'w') as f:
                f.write(response.read())

