
import pandas as pd
import numpy as np
import os
import re
import math

###############################################################################
# Settings

ns = [1, 2, 3, 4, 5]

# these should be the same as in download_and_extract_most_freq.py
year_start = 2010
year_end = 2019

# List of languages for which frequency lists should be extracted
langs = ["chinese_simplified", "english", "english-fiction", "french", "german", 
         "hebrew", "italian", "russian", "spanish"]
# each element has to be one of "english", "english-us", "english-gb", 
# "english-fiction", "chinese_simplified", "french", "german", 
# "hebrew", "italian", "russian", or "spanish"

# Final number of most frequent ngrams to keep for each n
number_of_most_freq = {"chinese_simplified": {1: 10000, 2: 5000, 3: 3000, 4: 1000, 5: 1000},
                       "english":            {1: 10000, 2: 5000, 3: 3000, 4: 1000, 5: 1000},
                       "english-fiction":    {1: 10000, 2: 5000, 3: 3000, 4: 1000, 5: 1000},
                       "french":             {1: 10000, 2: 5000, 3: 3000, 4: 1000, 5: 1000},
                       "german":             {1: 10000, 2: 5000, 3: 3000, 4: 1000, 5: 1000},
                       "hebrew":             {1: 10000, 2: 5000, 3: 2500, 4: 1000, 5:  400},
                       "italian":            {1: 10000, 2: 5000, 3: 3000, 4: 1000, 5: 1000},
                       "russian":            {1: 10000, 2: 5000, 3: 3000, 4: 1000, 5: 1000},
                       "spanish":            {1: 10000, 2: 5000, 3: 3000, 4: 1000, 5: 1000}}

# Number of most frequent ngrams to keep per file
per_file_number_of_most_freq = {"chinese_simplified": {1: 25000, 2: 25000, 3: 25000, 4: 25000, 5: 25000},
                                "english":            {1: 25000, 2: 5000, 3: 3000, 4: 3000, 5: 5000},
                                "english-fiction":    {1: 25000, 2: 5000, 3: 3000, 4: 3000, 5: 5000},
                                "french":             {1: 25000, 2: 5000, 3: 3000, 4: 3000, 5: 5000},
                                "german":             {1: 25000, 2: 5000, 3: 3000, 4: 3000, 5: 10000},
                                "hebrew":             {1: 25000, 2: 25000, 3: 25000, 4: 25000, 5: 25000},
                                "italian":            {1: 25000, 2: 5000, 3: 3000, 4: 3000, 5: 5000},
                                "russian":            {1: 25000, 2: 25000, 3: 25000, 4: 25000, 5: 25000},
                                "spanish":            {1: 25000, 2: 5000, 3: 3000, 4: 3000, 5: 5000}}


###############################################################################
# Constants etc.

langcode = {"english": "eng", "english-us": "eng-us", "english-gb": "eng-gb", 
            "english-fiction": "eng-fiction", "chinese_simplified": "chi_sim", 
            "french": "fre", "german": "ger", "hebrew": "heb", 
            "italian": "ita", "russian": "rus", "spanish": "spa"}

def totalcounts_1_file(lang):
    return f"source-data/data_googlebooks-{langcode[lang]}-20200217/totalcounts_1.txt"

def tmp_path(lang):

    path = f"ngrams/more/{lang}/tmp"

    if not os.path.exists(path):
        os.makedirs(path)

    return path

def per_gz_file_path(lang):

    path = f"ngrams/more/{lang}/most_freq_ngrams_per_gz_file"

    if not os.path.exists(path):
        os.makedirs(path)

    return path

def check_if_too_much_truncated(lang, n, d):

    if d.shape[0] < number_of_most_freq[lang][n]:

        raise Exception("Error: Not enough rows in outfile.\nNumber of rows in outfile:", d.shape[0], 
                "\nDesired number of rows:", number_of_most_freq[lang][n])

    elif d['freq'].iloc[number_of_most_freq[lang][n] - 1] <= max_min_freq_per_file:

        raise Exception("Error: Too few rows read per file.\nLowest frequency in outfile:", 
                d['freq'].iloc[number_of_most_freq[lang][n] - 1], "\nHighest frequency truncated at:", max_min_freq_per_file)


###############################################################################
# Functions

def gather_per_gz_files(lang, n):

    global max_min_freq_per_file

    files = [f for f in os.listdir(per_gz_file_path(lang)) if re.match(rf"^ngrams_{n}.*\.csv", f)]
    files.sort()

    d = list()
    for file in files:
        d += [pd.read_csv(per_gz_file_path(lang) + '/' + file,
                          nrows=per_file_number_of_most_freq[lang][n])]
        max_min_freq_per_file = max(d[-1]['freq'].iloc[-1], max_min_freq_per_file)

    d = pd.concat(d)
    d = d.sort_values(by=['freq'], ascending=False)
    d = d[~d.ngram.isnull()]  # remove empty ngrams
    d = d.reset_index(drop=True)

    check_if_too_much_truncated(lang, n, d)
    d[:number_of_most_freq[lang][n]].to_csv(f"ngrams/more/{lang}/{n}grams_{lang}_0_raw.csv", index=False)

    return d


def clean_remove_pos_tags(lang, n, d):

    pos_tags = "(?:VERB|NOUN|NUM|DET|ADV|ADJ|ADP|CONJ|PRON|PRT|X|\.|END|START)"

    # remove ngrams amongst whose words are free/wildcard part-of-speech tags
    d = d[~d.ngram.str.contains(rf'(?:^| )_{pos_tags}_(?: |$)')]

    if n > 1:
        # remove ngrams starting or ending with a punctuation "word"
        # such ngrams will appear in lower ngrams without the punctuation
        d = d[~d.ngram.str.contains(r' [\W_]+$')]
        d = d[~d.ngram.str.contains(r'^[\W_]+ ')]

        # this also captures misclassified punctuation
        d = d[~d.ngram.str.contains(rf' [\W_]+_{pos_tags}$')]
        d = d[~d.ngram.str.contains(rf'^[\W_]+_{pos_tags} ')]

    # for 1grams save a version that removes ngrams with no pos tags
    contains_pos = d.ngram.str.contains(rf'_{pos_tags}(?: |$)')
    if n == 1:
        check_if_too_much_truncated(lang, n, d[contains_pos])
        d[contains_pos].head(number_of_most_freq[lang][n]).to_csv(f"ngrams/more/{lang}/{n}grams_{lang}_1b_with_pos.csv", index=False)


    # remove ngrams with any pos tags
    d = d[~contains_pos]
    d = d.reset_index(drop=True)
    check_if_too_much_truncated(lang, n, d)
    d[:number_of_most_freq[lang][n]].to_csv(f"ngrams/more/{lang}/{n}grams_{lang}_1a_no_pos.csv", index=False)

    return d


def gather_and_clean():

    for lang in langs:

        print("language:", lang)

        for n in ns:

            print("n:", n)

            global max_min_freq_per_file
            max_min_freq_per_file = 0

            d = gather_per_gz_files(lang, n)
            clean_remove_pos_tags(lang, n, d)


###############################################################################
# run

if __name__ == '__main__':
    gather_and_clean()

