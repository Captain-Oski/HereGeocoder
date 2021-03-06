#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import pandas as pd
import requests
import logging
import time
from tqdm import tqdm

# Set your input file here
input_filename = raw_input("Enter the input file destination  : ")
# Set your output file name here.
output_filename = raw_input("Enter the output file destination  :")


logger = logging.getLogger('root')
logger.setLevel(logging.DEBUG)

# create console handler

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)

# ------------------ CONFIGURATION -------------------------------

# ---- HERE CONFIG ------#

APP_ID = ''
APP_CODE = ''

# ------------------ DATA LOADING --------------------------------

dataIn = pd.read_csv(input_filename)
df = pd.DataFrame(dataIn)

if 'Address' not in df.columns:
    raise ValueError('Missing Address column in input data')

# ------------------    FUNCTION DEFINITIONS ------------------------

def get_here_results(x, app_id, app_code):

    # Set up your Geocoding url

    geocode_url = 'https://geocoder.cit.api.here.com/6.2/geocode.json?searchtext={}'.format(x)
    geocode_url = geocode_url + '&app_id={}'.format(APP_ID)
    geocode_url = geocode_url + '&app_code={}'.format(APP_CODE)

    # Ping here for the reuslts:

    response = requests.get(geocode_url)

    # Results will be in JSON format - convert to dict using requests functionality

    response = response.json()
    answer = response['Response']['View'][0]['Result'][0]
    output = {
            'formatted_address': answer.get('Location').get('Address').get('Label'),
            'latitude': answer.get('Location').get('DisplayPosition').get('Latitude'),
            'longitude': answer.get('Location').get('DisplayPosition').get('Longitude'),
            'relevance': answer.get('Relevance'),
            'MatchLevel': answer.get('MatchLevel'),
            'MatchType': answer.get('MatchType')
            }
    # Append some other details:
    output['Addresse_Input'] = x
    return output

# ------------------ PROCESSING LOOP -----------------------------

results = []
errorResults= []
# Go through each address in turn
for index, row in tqdm(df.iterrows(), total=df.shape[0]):
    # While the address geocoding is not finished:
            x = row['Address']
            geocoded = False
            while geocoded is not True:

                # Geocode the address with here

                try:
					#append the good result in the result DataFrame
                    geocode_result = get_here_results(x, APP_ID, APP_CODE)
                    results.append(geocode_result)
                    logger.debug('OK : {}: {}'.format(x, 'OK'))
                    geocoded = True
                except Exception, e:
					#append the error result in the results DataFrame
                    results.append({
                        'Addresse_Input' : x,
                        'formatted_address': 'Invalid address input',
                        'latitude': 0,
                        'longitude': 0,
                        'relevance': 0,
                        'MatchLevel': 0,
                        'MatchType': 0
                        })
					#append the result in the errorResults DataFrame
                    errorResults.append({
                        'Addresse_Input' : x,
                        'formatted_address': 'Invalid address input',
                        'latitude': 0,
                        'longitude': 0,
                        'relevance': 0,
                        'MatchLevel': 0,
                        'MatchType': 0
                        })
                    logger.debug('ERROR: {}: {}'.format(x, 'UNSUCCESSFUL'))
                    geocoded = True

        #Every 1000 addresses, save progress to file
            if len(results) % 100 == 0:
                pd.DataFrame(results).to_csv("{}_bak".format(output_filename), encoding='utf-8')
                pd.DataFrame(errorResults).to_csv("{}_bak".format("errorResults.csv"), encoding='utf-8')

#calculate error results %
er = pd.DataFrame(errorResults)
gr = pd.DataFrame(results)
errorCount = len(er)
totalCount = len(gr)
totalPct = (float(errorCount) / float(totalCount))*100
accuracyMean = gr['relevance'].mean()

logger.info("Geocoding accuracy is : " + str(accuracyMean))

logger.info( str(totalPct) + "% Geocoding errors please refer to the errorResults log file" )

# Write the full errorResults to csv using the pandas library.
pd.DataFrame(errorResults).to_csv("errorResults.csv", encoding='utf-8')
# Write the full errorResults to csv using the pandas library.
rs = pd.DataFrame(results)
inpt = pd.DataFrame(dataIn)
# Merge the geocoded results with the input file (same order)
pd.concat([rs, inpt], axis=1).to_csv(output_filename, encoding='utf-8')
