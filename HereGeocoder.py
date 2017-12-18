import pandas as pd
import requests
import logging
import time


logger = logging.getLogger("root")
logger.setLevel(logging.DEBUG)
# create console handler
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)

#------------------ CONFIGURATION -------------------------------



#---- HERE CONFIG ------#
APP_ID = 'FznaQz9owNdr28wEanSu'
APP_CODE = 'rHHQFkXqgd60mdLvkE4sUg'
# Set your output file name here.
output_filename = 'output_here.csv'
# Set your input file here
input_filename = "input.csv"

#------------------ DATA LOADING --------------------------------

#data = pd.read_csv(input_filename, encoding='latin_1')
#data = pd.read_csv(input_filename, encoding='latin1')

dataIn = pd.read_csv(input_filename)
dataOut = pd.read_csv(output_filename)

df = pd.DataFrame(dataIn)

if 'Address' not in df.columns:
    raise ValueError("Missing Address column in input data")

# Form a list of addresses for geocoding:
# Make a big list of all of the addresses to be processed.



#------------------ FUNCTION DEFINITIONS ------------------------

def get_here_results(x, app_id, app_code):
    """
    Get geocode results from Google Maps Geocoding API.

    Note, that in the case of multiple google geocode reuslts, this function returns details of the FIRST result.

    @param address: String address as accurate as possible. For Example "18 Grafton Street, Dublin, Ireland"
    @param api_key: String API key if present from google.
                    If supplied, requests will use your allowance from the Google API. If not, you
                    will be limited to the free usage of 2500 requests per day.
    @param return_full_response: Boolean to indicate if yod like to return the full response from google. This
                    is useful if yod like additional location details for storage or parsing later.
    """
    # Set up your Geocoding url
    geocode_url = "https://geocoder.cit.api.here.com/6.2/geocode.json?searchtext={}".format(x)
    geocode_url = geocode_url + "&app_id={}".format(APP_ID)
    geocode_url = geocode_url + "&app_code={}".format(APP_CODE)


    # Ping here for the results:
    response = requests.get(geocode_url)
    # Results will be in JSON format - convert to dict using requests functionality
    response = response.json()

    #logger.debug("REPONSE RESULT=" + str(response['Response']['View'][0]['Result']))

    # if there's no results or an error, return empty results.
    if len(response['Response']['View'][0]['Result']) == 0:
        logger.debug("results == 0")
        output = {
            "formatted_address" : None,
            "latitude": None,
            "longitude": None,
            "accuracy": None,
            "google_place_id": None,
            "type": None,
            "postcode": None
        }
    else:
        #logger.debug("results different de 0")
        #logger.debug("---")
        #logger.debug("---")
        #logger.debug("---")
        #logger.debug("---")
        #logger.debug("---")

        answer = response['Response']['View'][0]['Result'][0]

        #logger.debug(answer)


        output = {
            "formatted_address" : answer.get('Location').get('Address').get('Label'),
            "latitude": answer.get('Location').get('DisplayPosition').get('Latitude'),
            "longitude": answer.get('Location').get('DisplayPosition').get('Longitude'),
            "relevance": answer.get('Relevance'),
            "MatchLevel" : answer.get('MatchLevel'),
            "MatchType" : answer.get('MatchType'),

        }

    # Append some other details:
    output['Addresse_Input'] = x
    #if return_full_response is True:
    #output['response'] = results
    #['banniere'] = banniere

    return output

#------------------ PROCESSING LOOP -----------------------------

# Ensure, before we start, that the API key is ok/valid, and internet access is ok
#test_result = get_here_results("Montreal", API_KEY, RETURN_FULL_RESULTS)
#if (test_result['status'] != 'OK') or (test_result['formatted_address'] != 'London, UK'):
#    logger.warning("There was an error when testing the Google Geocoder.")
#    raise ConnectionError('Problem with test results from Google Geocode - check your API key and internet connection.')

# Create a list to hold results
results = []


# Go through each address in turn
for index, row in df.iterrows():
    # While the address geocoding is not finished:
    x = row['Address']
    geocoded = False
    while geocoded is not True:
        # Geocode the address with here
        try:

            geocode_result = get_here_results(x, APP_ID, APP_CODE)
            #logger.debug(address)
        except Exception as e:
            logger.exception(e)
            logger.error("Major error with {}".format(x))
            logger.error("Skipping!")
            geocoded = True


        # If we're over the API limit, backoff for a while and try again later.
        # if geocode_result['status'] == 'OVER_QUERY_LIMIT':
        #    logger.info("Hit Query Limit! Backing off for a bit.")
        #    time.sleep(BACKOFF_TIME * 60) # sleep for 30 minutes
        #    geocoded = False
        #else:
            # If we're ok with API use, save the results
            # Note that the results might be empty / non-ok - log this
        #if geocode_result['status'] != 'OK':
        #        logger.warning("Error geocoding {}: {}".format(address, geocode_result['status']))
        logger.debug("Geocoded: {}: {}".format(x, "OK"))
        results.append(geocode_result)
        geocoded = True

    # Print status every 100 addresses
    #if len(results) % 100 == 0:
        #logger.info("Completed {} of {} address".format(len(results), len(addresses)))

    # Every 500 addresses, save progress to file
    #if len(results) % 500 == 0:
        #pd.DataFrame(results).to_csv("{}_bak".format(output_filename))

# All done
logger.info("Finished geocoding all addresses")
# Write the full results to csv using the pandas library.
pd.DataFrame(results).to_csv(output_filename, encoding='utf-8')
# Merge the geocoded results with the input file (same order)
pd.concat([dataOut, dataIn], axis=1).to_csv(output_filename)
