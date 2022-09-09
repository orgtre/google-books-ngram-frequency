
from cmath import nan
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
langs = ["chinese_simplified", "english", "english-fiction", "french", "german", "hebrew", "italian", "russian", "spanish"]
## each element has to be one of "english", "english-us", "english-gb", 
## "english-fiction", "chinese_simplified", "french", "german", 
## "hebrew", "italian", "russian", or "spanish"

# Final number of most frequent ngrams to keep for each n
number_of_most_freq = {"chinese_simplified": {1: 10000, 2: 5000, 3: 3000, 4: 1000, 5: 1000},
                       "english":            {1: 10000, 2: 5000, 3: 3000, 4: 1000, 5: 1000},
                       "english-fiction":    {1: 10000, 2: 5000, 3: 3000, 4: 1000, 5: 1000},
                       "french":             {1: 10000, 2: 5000, 3: 3000, 4: 1000, 5: 1000},
                       "german":             {1: 10000, 2: 5000, 3: 3000, 4: 1000, 5: 1000},
                       "hebrew":             {1: 10000, 2: 5000, 3: 1000, 4: 200, 5:  80},
                       "italian":            {1: 10000, 2: 5000, 3: 3000, 4: 1000, 5: 1000},
                       "russian":            {1: 10000, 2: 5000, 3: 3000, 4: 1000, 5: 1000},
                       "spanish":            {1: 10000, 2: 5000, 3: 3000, 4: 1000, 5: 1000}}

# Number of most frequent ngrams to keep per file
per_file_number_of_most_freq = {"chinese_simplified": {1: 40000, 2: 25000, 3: 25000, 4: 25000, 5: 25000},
                                "english":            {1: 25000, 2: 5000, 3: 3000, 4: 3000, 5: 5000},
                                "english-fiction":    {1: 40000, 2: 10000, 3: 3000, 4: 3000, 5: 5000},
                                "french":             {1: 25000, 2: 5000, 3: 3000, 4: 3000, 5: 5000},
                                "german":             {1: 25000, 2: 5000, 3: 3000, 4: 10000, 5: 20000},
                                "hebrew":             {1: 50000, 2: 50000, 3: 50000, 4: 50000, 5: 50000},
                                "italian":            {1: 25000, 2: 5000, 3: 3000, 4: 3000, 5: 10000},
                                "russian":            {1: 25000, 2: 25000, 3: 25000, 4: 25000, 5: 25000},
                                "spanish":            {1: 25000, 2: 5000, 3: 3000, 4: 3000, 5: 5000}}


###############################################################################
# Constants etc.

all_langs = ["chinese_simplified", "english", "english-fiction", "french", "german", 
         "hebrew", "italian", "russian", "spanish"]

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

def extra_1grams_to_exclude_file(n):
    return f"source-data/extra_ngrams_to_exclude/extra_{n}grams_to_exclude.csv"

def check_if_too_much_truncated(lang, n, d):

    global max_min_freq_per_file
    
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


def split_contractions(d, dother):
    '''Split contractions in the ngram column of 'd' append the resulting 
    larger n-grams to the corresponding dataframe in 'dother'.
    Examples of contractions are qu'il and c'est.
    Return a touple of the modified 'd' and 'dother'.'''

    dt = d.ngram.str.split(" ", expand=True)
    n = dt.shape[1]

    dt2s = []
    for i in range(dt.shape[1]):
        dt2s.append(dt[i].str.split(r"(.*?')", expand=True))
    dt2 = pd.concat(dt2s, axis=1)
    dt2 = dt2.replace("", None)

    idx = (dt2.values == None).argsort(axis=1)
    dt3 = pd.DataFrame(
        dt2.values[np.arange(dt2.shape[0])[:, None], idx],
        index=dt2.index,
        columns=dt2.columns)

    nwords = dt3.apply(lambda x: (~x.isnull()).sum(), axis='columns')

    dt4 = dt3.fillna(value="")
    dt4 = dt4.apply(' '.join, axis=1)
    dt4 = dt4.apply(lambda x: (x.strip()))

    d.ngram = dt4

    # add the ngrams which now have other than n words to dother
    for i in set(np.unique(nwords).tolist()) - {n}:
        dother[i] = pd.concat([dother[i], d[nwords == i]])

    d = d[nwords == n]

    return d, dother


def split_2grams_to_1grams(d2):

    dt = d2.ngram.str.split(" ", expand=True)
    n = dt.shape[1]

    dt = dt.stack(dropna=False)
    dt = dt.reset_index(level=[0,1], drop=True)

    df = pd.DataFrame(np.repeat(d2.freq.values, n, axis=0))

    dt = pd.concat([dt, df], axis=1)
    dt.columns = ["ngram", "freq"]

    return dt


def merge_upcase_lowcase(d, cutoff):
    '''Combine words with different capitalization. 
    E.g. il - Il, le - Le, je - Je, etc.
    Merges capitalized entries to non-capitalized ones unless 
    the share capitalized is at least cutoff.
    cutoff = 0.92 is a good value for French.
    For German this works too.'''

    first_letter = d['ngram'].str[:1]
    later_letters = d['ngram'].str[1:]
    dup = d.loc[first_letter.str.isupper(), ['ngram', 'freq']]
    dup['ngramlow'] = first_letter.loc[first_letter.str.isupper()].str.lower() + later_letters.loc[first_letter.str.isupper()]
    # merging it like this ignores words that are all cap, since they'd cause problems later and are few enough to ignore

    del first_letter
    del later_letters

    dup = dup.rename(columns={"ngram": "ngramup", "freq": "frequp"})

    dup = pd.merge(dup, d, left_on=["ngramlow"], right_on=["ngram"])
    del dup['ngramlow']

    dup['shareup'] = dup.frequp / (dup.frequp + dup.freq)
    # dup.sort_values(by=['shareup'], ascending=False).to_csv(f"{tmp_path(lang)}/ngrams_{n}_tmp.csv", index=False)
    # if above cutoff remain large, otherwise merge with small


    # merging this properly

    dup['freq'] += dup['frequp']

    upcase_to_remove = dup[dup.shareup < cutoff][['ngramup']]
    lowcase_to_remove = dup[dup.shareup >= cutoff][['ngram']]
    freqs_to_update = dup[['ngram', 'freq']]

    del dup


    # removes rows matched from upcase_to_remove

    d = d.merge(upcase_to_remove, left_on=['ngram'], right_on=['ngramup'],
                    how='left', indicator=True)
    d = d[d._merge == "left_only"]
    del d['_merge']
    del d['ngramup']
    del upcase_to_remove


    # removes rows matched from lowcase_to_remove

    d = d.merge(lowcase_to_remove, left_on=['ngram'], right_on=['ngram'],
                    how='left', indicator=True)
    d = d[d._merge == "left_only"]
    del d['_merge']
    del lowcase_to_remove


    # update freqs

    d = d.merge(freqs_to_update, on=['ngram'], how='left')
    d['freq'] = d['freq_y'].fillna(d['freq_x']).astype('int')
    d = d.drop(['freq_x', 'freq_y'], axis=1)
    d = d.sort_values(by=['freq'], ascending=False).reset_index(drop=True)

    del freqs_to_update

    return d



def remove_pattern(d, pattern, exceptions=[]):
    '''Look for regex 'pattern' and remove matching ngrams,
    except if they are in list 'exceptions'.'''
    global freq_words_removed
    if exceptions != []:
        freq_words_removed += d[(d.ngram.str.contains(pattern)) & (~d['ngram'].isin(exceptions))].freq.sum()
        d = d[(~d.ngram.str.contains(pattern)) | (d['ngram'].isin(exceptions))]
    else:
        freq_words_removed += d[d.ngram.str.contains(pattern)].freq.sum()
        d = d[~d.ngram.str.contains(pattern)]
    return d


def replace_pattern_and_group(d, pattern, replacement):
    '''Replace 'pattern' in d.ngram with 'replacement'. 
    Group resulting entries by the value of d.ngram and 
    add frequencies within groups.'''
    d.ngram = d.ngram.str.replace(pattern, replacement, regex=True)
    d = d.groupby("ngram")[["freq"]].sum()
    d.reset_index(level=0, inplace=True)
    d = d.sort_values(by=['freq'], ascending=False).reset_index(drop=True)
    return d

def remove_entries(d, entries):
    '''Remove 'entries', updating 'freq_words_removed'.'''
    global freq_words_removed
    freq_words_removed += d[d['ngram'].isin(entries)].freq.sum()
    d = d[~d['ngram'].isin(entries)]
    return d


def gather_and_clean(lang, n):
    
    global max_min_freq_per_file
    max_min_freq_per_file = 0

    global freq_words_added
    freq_words_added = 0

    global freq_words_removed
    freq_words_removed = 0

    # dictionary of dataframes to hold ngrams to be added at other n
    df_empty = pd.DataFrame({'ngram' : [], 'freq' : []})
    dother = {key: df_empty for key in range(1, 11)}

    
    # gather ngrams
    d = gather_per_gz_files(lang, n)

    
    # remove part-of-speech tags
    d = clean_remove_pos_tags(lang, n, d)


    # split contractions

    if lang == 'french':

        d, dother = split_contractions(d, dother)

        ## add the parts of the 2-grams resulting from split back as 1-grams

        if n == 1:
            freq_words_added += sum(dother[2].freq)
            dadd = split_2grams_to_1grams(dother[2])
            d = pd.concat([d, dadd], axis=0)
            d = d.groupby("ngram")[["freq"]].sum()
            d.reset_index(level=0, inplace=True)
            d = d.sort_values(by=['freq'], ascending=False).reset_index(drop=True)            
            dother[2] = df_empty


    # handle entries ending with "_"

    d = replace_pattern_and_group(d, pattern=r"_$", replacement="")


    # merge upcase and lowcase

    d = merge_upcase_lowcase(d, 0.92)


    # save copy of data before starting to remove entries
    dfull = d


    # remove entries with only punctuation and numbers

    punctuation_and_numbers_regex = r"^[ _\W0-9]+$"
    d = remove_pattern(d, punctuation_and_numbers_regex)


    # handle uppercase words

    upcases_to_keep = {key: [] for key in all_langs}
    upcases_to_keep['german'] = ["DDR", "AG", "BRD"]
    upcases_to_keep['english'] = ["I", "God", "American", "English", "Jesus", "British", "European",
                                  "America", "French", "China", "German", "Europe", "Christ", "England",
                                  "Chrstian", "Bible", "June", "Chinese", "India", "July", "African",
                                  "April", "January", "September", "Indian", "December", "Africa",
                                  "October", "August", "Germany", "Israel", "November", "February",
                                  "Americans", "UK", "California", "Jewish", "Japan", "Canada",
                                  "Japanese", "Britain", "Greek", "Roman", "Russian", "Spanish"]
    upcases_to_keep['english-fiction'] = upcases_to_keep['english']
    upcases_to_keep['french'] = ["France", "Europe", "Afrique", "Allemagne", "Londres", "Angleterre",
                                 "Italie", "Amérique", "Chine", "Espagne", "Israël", "Russie", "Noël",
                                 "Canada", "Orient", "Bretagne", "Bruxelles", "Algérie", "Inde", "Asie",
                                 "Belgique", "Égypte", "Occident", "Japon", "Congo", "Maroc", "Moscou",
                                 "Autriche", "Brésil", "Venise", "Pologne", "Platon", "Moïse", "Aristote",
                                 "Cameroun" "Turquie", "Provence", "Sénégal", "Méditerranée", "Mexique",
                                 "Syrie", "American", "Australie", "Athènes", "Alpes", "Suède", "Grèce",
                                 "Normandie", "Tunisie", "Liban", "Socrate", "Hongrie", "Alsace", "Guinée",
                                 "Rhin", "Californie", "Palestine", "Indes", "Barcelone", "Danemark",
                                 "Munich", "Arabie", "Norvège", "Roumanie", "Lénine", "Maghreb", "Indochine",
                                 "Beyrouth", "Pérou", "Finlande", "Libye", "Soudan", "Colombie", "Haïti",
                                 "URSS", "ADN", "ONU",
                                 "'S"]
    # d[d.ngram.str.contains(r"[A-ZÀ-Ü]")].to_csv(f"{tmp_path(lang)}/ngrams_{n}_tmp.csv", index=False)
    # checked for for words to keep up to entry 1000

    if n == 1:
        if lang in ['german']:
            upcase_regex = r"^[A-ZÀ-Ü]+$"
        else:
            upcase_regex = r"[A-ZÀ-Ü]"            
        d = remove_pattern(d, upcase_regex, upcases_to_keep[lang])


    # remove most one-character words

    onechars_to_keep = {key: [] for key in all_langs}
    onechars_to_keep['english'] = ["a", "I"]
    onechars_to_keep['english-fiction'] = onechars_to_keep['english']
    onechars_to_keep['french'] = ["à", "a", "y"]
    onechars_to_keep['russian'] = ["а", "б", "в", "ж", "и", "к", "о", "с", "у", "я"]

    if lang != 'chinese_simplified':        
        onechar_regex = r"^.$"
        d = remove_pattern(d, onechar_regex, onechars_to_keep[lang])


    # remove contractions for some langagues
    # TODO remove for other languages too?
    if lang in ['german', 'russian']:
        d = remove_pattern(d, r"'")

    if lang in ['english-fiction']:
        d = remove_pattern(d, r"^'")    


    # remove entries with non-word characters other than "'" and " "
    # TODO this needs to be changed, especially for n-grams with n > 1
    if lang == 'russian':
        nonword_regex = r"[^\w' -,]"
    else:
        nonword_regex = r"[^\w' ,]"
        d = remove_pattern(d, nonword_regex)


    # remove entries with numbers
    d = remove_pattern(d, r"[0-9]")


    # manually remove any remaining unwanted ngrams
    # e.g. names of persons, wrong language words, some abbrevations without a dot, copyright notices    
    extra_ngrams_to_exclude = \
        {key: pd.read_csv(extra_1grams_to_exclude_file(key)).to_dict('list') for key in ns}    
    d = remove_entries(d, extra_ngrams_to_exclude[n][lang])


    # save dataframe of removed words
    drem = dfull[~dfull.ngram.isin(d.ngram)]
    drem = drem.sort_values(by=['freq'], ascending=False).reset_index(drop=True)
    drem = drem[drem.freq >= d.iloc[number_of_most_freq[lang][n]-1, 1]]
    drem.to_csv(f"ngrams/more/{lang}/{n}grams_{lang}_2_removed.csv", index=False)

    
    # save final output
    d = d.sort_values(by=['freq'], ascending=False).reset_index(drop=True)
    check_if_too_much_truncated(lang, n, d)
    d[:number_of_most_freq[lang][n]].to_csv(f"ngrams/{n}grams_{lang}.csv", index=False)

    


def gather_and_clean_all():

    for lang in langs:

        print("language:", lang)

        for n in ns:

            print("n:", n)

            gather_and_clean(lang, n)
            


###############################################################################
# run

if __name__ == '__main__':
    gather_and_clean_all()


###############################################################################

