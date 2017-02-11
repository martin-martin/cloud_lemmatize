
# coding: utf-8
##############################################################################
############################## Do the pipeline! ##############################
##############################################################################
# Final sprint for language one!

import os
import re
import json
import time
import logging
import pandas as pd
from pprint import pprint


##################### Collecting files and setting up logging #################
# defining the language being processed (influences file location and output!)
language = "fr"
###############################################################################


# set up logging
start = time.time()
FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT,
                    filename='{0}.log'.format(language),
                    level=logging.DEBUG)

folder = "chunk_out"
logging.info("====================BEGIN PROCESSING {} FILES====================".format(language))
all_files = os.listdir("{0}/{1}".format(folder, language))

# fetch everything before the first occurance of a opening curly brace
# to remove HTTP response headers present in the files
pattern = re.compile(r"[^{]*")

# clean up the data files for JSON traversion
documentation = ""
response_list = list()

for a_file in all_files:
    # fetch the current file
    with open("{0}/{1}/{2}".format(folder, language, a_file)) as f:
        file_string = f.read()
        header = re.search(pattern, file_string)
        documentation += "\t{0}\n\n{1}".format(a_file, header.group(0))
        # delete the HTML response header from the JSON
        file_string = file_string.replace(header.group(0), "")
        # load the JSON into a python dict
        response = json.loads(file_string)
        response_list.append(response)

# saving the documentation headers, just because
with open("{0}doc_headers.txt".format(language), "w") as f:
    f.write(documentation)
logging.info("*FINISHED WRITING HEADER DOCUMENTATION FILE*")



############################# Finding the pieces #############################

def item_generator(json_input, lookup_key):
    """traverses the JSON structure to find entries with specific key names."""
    if isinstance(json_input, dict):
        for k, v in json_input.items():
            if k == lookup_key:
                yield v
            else:
                for child_val in item_generator(v, lookup_key):
                    yield child_val
    elif isinstance(json_input, list):
        for item in json_input:
            for item_val in item_generator(item, lookup_key):
                yield item_val


# a place to collect all the response that I want to deal with
focus_list = list()
for i, response in enumerate(response_list):
    now = time.time()
    logging.info("processing file {0}".format(i))
    # '_[0]' takes the first entry of an 'analysis_list' object
    # later entries are regarding different potential
    # semantical meanings and might be interesting
    # for another time and type of analysis
    # the first entry holds all the information we currently need
    for _ in item_generator(response, "analysis_list"):
        # ATTENTION:
        # meaningcloud also analyzes 'phrases', grouping specific words together
        # for now I take only those forward that are actually single words
        # the 'phrases' are only groups of single words, meaning that every word
        # that appears in a 'phrase' does also appear as a single word
        # since that's the unit we're dealing with, I only collect the single words
        #
        # if original form consists of more than one word there is a space present
        # therefore searching for " " would not return '-1' (= 'not found')
        if _[0]["original_form"].find(" ") == -1:
            focus_list.append(_[0])
    logging.info("finished processing file {0} in {1} magical time units".format(i, time.time()-now))



#################### Propping the data into a nice format ####################

df = pd.DataFrame(focus_list)

# keeping only the the columns we need now
fdf = df[['lemma', 'original_form', 'tag']]

# exporting to a csv file
fdf.to_csv("lemmatizationTagged/{}_lemPOS.csv".format(language), encoding="utf-8")

logging.info("====================FINISHED====================")
logging.info("Processed {0} files, took {1} special time units".format(len(all_files), time.time() - start))