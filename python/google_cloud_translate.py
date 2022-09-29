# Translate the lists of ngrams in folder 'ngrams' using Google Cloud Translate
# and add the results as a column to the corresponding csv-file

# This requires a Google Cloud Translate API key. Follow these steps to set up
# everything on the Google Cloud side:
# https://cloud.google.com/translate/docs/setup

# As of writing this, the first 500,000 characters per month are free. After
# this the cost is $20/million characters. As an example, the 10,000 Spanish
# 1-grams take up around 76,000 characters. Translating the 10,000 most
# common 1-grams of each non-English language to English was charged by Google
# as around 483,000 characters.

import pandas as pd
from pathlib import Path
from google.cloud import translate_v2 as translate


###############################################################################
# Settings

# List of n-grams for which translations should be added:
# ns = [1, 2, 3, 4, 5]
ns = [1]

# List of languages for which translations should be added:
langs = ["chinese_simplified", "french",
         "german", "hebrew", "italian", "russian", "spanish"]
## each element has to be one of "english",
## "english-fiction", "chinese_simplified", "french", "german", 
## "hebrew", "italian", "russian", or "spanish"

# Language to translate to:
outlang = "english"
# should be one of the langugues allowed above

add_equal_indicator = False
# whether to add an indicator when the translation equals the input
# (Google translate returns the input when no translation is found)

test_run = True
# whether to just run on the first three ngrams and save output separately
# otherwise the full infile is translated and a column with results is added


###############################################################################
# Constants etc.

langiso = {"english": "en", "english-us": "en", "english-gb": "en", 
            "english-fiction": "en", "chinese_simplified": "zh-CN", 
            "french": "fr", "german": "de", "hebrew": "iw", 
            "italian": "it", "russian": "ru", "spanish": "es"}

def ngramlist_path(n, lang):
    return f"ngrams/{n}grams_{lang}.csv"


###############################################################################
# Functions

def translate_text(text, target, source):
    """Translates text from source language into target language.
    
    Target and source must be ISO 639-1 language codes.
    https://googleapis.dev/python/translation/latest/client.html
    """
    translate_client = translate.Client()

    # Text can also be a sequence of strings, in which case this method
    # will return a sequence of results for each text.
    result = translate_client.translate(text, target_language=target,
                                        source_language=source)
    
    # Note: If no translation found it just returns the input.
    return result


def translate_long_list(inlist, target, source):
    """Translates inlist of text using the 'translate_text' function.

    The maximum number of strings in 'translate_text' is 128.
    Hence this function splits inlist and calls 'translate_text'
    on each part separately, collecting the results.
    See 'translate_text' for target and source specification.
    """
    print(f"Translating {len(''.join(inlist))} characters.")

    nstrings = 128
    result = []
    for i in range(0, len(inlist), nstrings):
        sub = inlist[i:i+nstrings]
        result = result + translate_text(sub, target, source)

    return result


def fix_case(arr, outlang):
    """Fix the case of the strings in array 'arr' and return it.

    The list of 1-grams in language 'outlang' is used to set the case.
    """
    reffile = ngramlist_path(1, outlang)
    dr = pd.read_csv(reffile)
    for i in range(len(arr)):
        if arr[i] not in dr.ngram.values and len(arr[i]) > 0:
            swapped = arr[i][0].swapcase() + arr[i][1:]
            if swapped in dr.ngram.values:
                arr[i] = swapped
            else:
                split = arr[i].split(" ")
                lower = [s.lower() for s in split]
                if len(split) > 1 and split[0] != lower[0]:
                    if len(split) > 2:
                        if split[1] == lower[1] and split[2] == lower[2]:
                            if lower[0] in dr.ngram.values:
                                arr[i] = ' '.join([lower[0]] + split[1:])
                    else:
                        if split[1] == lower[1]:
                            if lower[0] in dr.ngram.values:
                                arr[i] = ' '.join([lower[0]] + split[1:])
    return arr


def ngramlist_add_translation(n, lang, outlang):

    infile = ngramlist_path(n, lang)
    d = pd.read_csv(infile)
    
    if test_run:
        outfile = (str(Path(infile).parent) + "/"
                   + Path(infile).stem + "_test" + Path(infile).suffix)
        d = d[0:3]
    else:
        outfile = infile
        
    inlist = d['ngram'].to_list()

    result = translate_long_list(inlist,
                                 target=langiso[outlang],
                                 source=langiso[lang])
    
    d[langiso[outlang]] = [i['translatedText'] for i in result]
    
    # Fix: Google returns "'" as "&#39;" for some reason
    d[langiso[outlang]] = d[langiso[outlang]].fillna(value="")
    d[langiso[outlang]] = (d[langiso[outlang]]
                           .str.replace("&#39;", "'", regex=False))
    
    # Fix: Google often returns the wrong case
    d[langiso[outlang]] = fix_case(d[langiso[outlang]].values,
                                   outlang)
    
    if add_equal_indicator:
        d.loc[d['ngram'] == d[langiso[outlang]], 'equal'] = "1"
        d.loc[d['ngram'] != d[langiso[outlang]], 'equal'] = ""
    
    d.to_csv(outfile,index=False, header=True)

    
def ngramlist_add_translation_all(ns, langs, outlang):
    
    if outlang in ["english", "english-fiction"]:
        if "english" in langs:
            langs.remove("english")
        if "english-fiction" in langs:
            langs.remove("english-fiction")
    else:
        if outlang in langs:
            langs.remove(outlang)
            
    for lang in langs:
        
        print("language:", lang)
        
        for n in ns:
            
            print("n:", n)
            
            ngramlist_add_translation(n, lang, outlang)


###############################################################################
# Run

if __name__ == '__main__':
    ngramlist_add_translation_all(ns, langs, outlang)
