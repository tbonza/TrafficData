""" Figuring out which coordinates map to which roads

The goal is to find a consensus between pair_definitions.csv and
the reverse geocoding api from geocache. Both approaches were used
because each approach includes incomplete information.

For example, 'pair_id' '10599' gives a 'Description' for the location
as '6WB-MM055.9'.

However, most descriptions are something like 'I-90 WB after on-ramp
(Newton Corner)'. Pretty helpful, we can parse some things out with
regular expressions and reasonably conclude that this point is located
on 'I-90'. When we plug in the pair_id, '10498', to the geocode api,
we find that 'I-90', is also returned.

It's also important to know that Ids don't match across the three
datasources we have available. There's not much we can do about it.
The solution is to just use what's in the xml as the point of
departure. Otherwise, we have no way of attaching coordinates to
the data. We should just acknowledge these data points as 'dead'
and have a funeral.
"""
import os
import io
import re
import csv
import json
import time
import logging
from collections import Counter

from checkPairId import datasources, enable_log

def read_json():
    """ Reading in json data from geocode api 

    json data is based on pair_routes.xml

    Bypassing tests that the user is in the correct directory because
    they should have figured it out by now.
    """
    da_path = os.path.abspath("")+ "/post1/src/geocode.txt"
    # needs to support utf-8
    with io.open(da_path, 'r', encoding="utf-8") as f:
        logging.info("Read json file into memory")
        return json.load(f)

def use_correct_csv_column(datasource):
    """ Let's make sure we're grabbing the correct columns
    
    Returns:
        Tuple, pair_id, Description from pair_definitions.csv
    """
    logging.info("Indexed row for reading csv file")
    return (datasource.index("pair_id"),
            datasource.index("Description"))
    
def read_description(datasources):
    """ Returns pair_id mapped to description
    from pair_definitions.csv"""
    # timing function
    start = time.time()
    # path to data
    junk, datasource, junk = datasources
    pair_definitions = {}
    with open(datasource, 'rb') as f:
        header = True
        reader = csv.reader(f, delimiter = ",")
        # attempt to return a list of strings, where each string
        # is a pairID
        try:
            for row in reader:
                if header == True:
                    logging.info("Read in header of csv")
                    pair_id, definition = use_correct_csv_column(row)
                    header = False
                else:
                    pair_definitions[row[pair_id]]=row[definition]
        except csv.Error as e:
            logging.critical('datasource %s, line %d: %s' %
                             (datasource, reader.line_num, e))
    logging.info("Elapsed time for parse: " + str(time.time() - start))
    return pair_definitions

def parse_description(datasource):
    """ Just don't try to regex pair_definitions.csv. It's a mess.
    Compare the reverse geocoding to the descriptions given but like
    don't go down this road. Life is too short. """
    pass

def nearest_highway(geocode_json):
    """ Finds the nearest highway

    Args:
        geocode_json: Geocode api written to json; can be accessed
                      using read_json()
    Returns:
        Dict, str, pair_id mapped onto the nearest highway
    """
    logging.info("STARTED - Nearest highway comparisons")
    for pair_id in geocode_json.keys():
        count = 0
        logging.info("Using pair_id: "+ str(pair_id))
        while count < len(geocode_json[pair_id][0]):
            first = True
            agree = "None"
            
            c = Counter(geocode_json[pair_id][0][count])
            road, num = c.most_common(1)[0]
            logging.info(agree)
            logging.info(road)
            if first:
                logging.info("Set first most common road to itself")
                road = agree
                first = False
                
            elif road != agree:
                logging.info("Using list number: " + str(count))
                logging.critical(str(agree) + " is not equal to " +\
                                 str(road))
                
            elif road == agree:
                logging.info("Using list number: " + str(count))
                logging.info(str(agree) + " is equal to " +str(road))

            else:
                logging.critical("Trouble in paradise")
            logging.critical(str(count))
            count += 1
    logging.info("FINISHED - Nearest highway comparisons")

        
def write_csv_file(datasource):
    """ Output, (pair_id, Route)
    """
    pass

def main():
    nearest_highway(read_json())

if __name__ == "__main__":
    enable_log("highwayFinder")
    main()
