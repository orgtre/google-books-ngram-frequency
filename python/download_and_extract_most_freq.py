# Extract the most frequent ngrams from Google Books data
# https://storage.googleapis.com/books/ngrams/books/datasetsv3.html

import pandas as pd
import wget, gzip, os, re
import multiprocessing as mp
from timeit import default_timer as timer
from urllib.request import urlopen
from functools import partial

###############################################################################
# Settings

# List of the n's in 'ngram' for which frequency lists are wanted,
# i.e. a list of integers between 1 and 5
ns = [1, 2, 3, 4, 5]

# List of languages for which frequency lists should be extracted
langs = ["chinese_simplified", "english", "english-fiction", "french", "german", 
         "hebrew", "italian", "russian", "spanish"]
# each element has to be one of "english", "english-us", "english-gb", 
# "english-fiction", "chinese_simplified", "french", "german", 
# "hebrew", "italian", "russian", or "spanish"


# Only consider books published from this year on
year_start = 2010

# Only consider books published up to and including this year
year_end = 2019

# When processing each .gz individual file, for each n,
# discard ngrams occurring less frequently than given here;
# should be chosen small enough so that none of the 'number_of_most_freq'
# most frequent ngrams are discarded; however,
# the code will run faster the larger these numbers
min_freq_to_keep = {1: 1000, 2: 1000, 3: 1000, 4: 1000, 5: 1000}

# Final number of most frequent ngrams to keep for each n
number_of_most_freq = {1: 10000, 2: 5000, 3: 3000, 4: 1000, 5: 1000}

# Make sure we are in right repository when running code (other paths are relative)
# os.chdir("my-path-to/google-books-ngram-frequency")

# Number of cores to run on in parallel
# number_of_cores = mp.cpu_count() - 2
number_of_cores = 1

# Redownload and reprocess gz files for which a list of most common ngrams
# already exists
redownload_files = False

# Continue with next file once an exception is thrown handling a file,
# just listing the files not handled properly;
# the alternative is to throw the exception
continue_on_exception = True

# Toggle use of the below custom lists of urls to actually download
use_custom_url_indices = True

# Indices of urls to actually download (same as file numbers in filenames,
# see https://storage.googleapis.com/books/ngrams/books/datasetsv3.html)
# This excludes files with only ngrams not starting with a letter,
# but for chi, fre, rus, and ger those starting with _START_ are included
custom_url_indices = {"spanish":
                      {1: [*range(0, 3)],
                       2: [*range(6, 23)] + [*range(25, 73)],
                       3: [*range(45, 131)] + [*range(222, 231)] + [*range(239, 688)],
                       4: [*range(33, 81)] + [*range(230, 245)] + [*range(262, 571)],
                       5: [*range(78, 163)] + [*range(668, 701)] + [*range(771, 1415)]},
                      "chinese_simplified":
                      {1: [*range(0, 1)],
                       2: [*range(0, 6)],
                       3: [*range(11, 59)],
                       4: [*range(15, 46)],
                       5: [*range(45, 49)] + [*range(57, 105)]},
                      "russian":
                          {1: [*range(0, 2)],
                           2: [*range(9, 69)],
                           3: [*range(118, 126)] + [*range(139, 471)],
                           4: [*range(125, 136)] + [*range(150, 313)],
                           5: [*range(311, 334)] + [*range(373, 633)]},
                      "french":
                      {1: [*range(0, 6)],
                       2: [*range(9, 36)] + [*range(41, 115)],
                       3: [*range(81, 227)] + [*range(368, 380)] + [*range(398, 1161)] +
                          [*range(1167, 1197)],
                       4: [*range(67, 154)] + [*range(406, 429)] + [*range(464, 1104)],
                       5: [*range(178, 347)] + [*range(1328, 1395)] + [*range(1547, 3000)] +
                          [*range(3010, 3071)]},
                      "german":
                          {1: [*range(0, 8)],
                           2: [*range(12, 92)] + [*range(104, 181)],
                           3: [*range(99, 517)] + [*range(739, 753)] + [*range(770, 1369)],
                           4: [*range(67, 274)] + [*range(576, 600)] + [*range(628, 1003)],
                           5: [*range(151, 482)] + [*range(1360, 1419)] + [*range(1520, 2262)]},
                      "english":
                          {1: [*range(6, 24)],
                           2: [*range(85, 278)] + [*range(317, 589)],
                           3: [*range(671, 2085)] + [*range(3038, 6863)] + [*range(6873, 6877)],
                           4: [*range(515, 1389)] + [*range(3207, 6660)] + [*range(6664, 6667)],
                           5: [*range(1312, 3120)] + [*range(10447, 19407)] + [*range(19416, 19420)]},
                      "english-fiction":
                          {1: [*range(0, 1)],
                           2: [*range(1, 47)],
                           3: [*range(31, 110)] + [*range(188, 549)],
                           4: [*range(28, 77)] + [*range(227, 515)],
                           5: [*range(80, 181)] + [*range(758, 1449)]},
                      "hebrew":
                          {1: [*range(0, 1)],
                           2: [*range(0, 10)],
                           3: [*range(16, 45)],
                           4: [*range(14, 25)],
                           5: [*range(27, 42)]},
                      "italian":
                          {1: [*range(0, 2)],
                           2: [*range(4, 16)] + [*range(19, 60)],
                           3: [*range(35, 94)] + [*range(185, 553)],
                           4: [*range(26, 57)] + [*range(202, 427)],
                           5: [*range(59, 108)] + [*range(558, 984)]}
                      }


###############################################################################
# Constants etc.

max_relevant_year_freqs = 2019 - year_start + 1

langcode = {"english": "eng", "english-us": "eng-us", "english-gb": "eng-gb", 
            "english-fiction": "eng-fiction", "chinese_simplified": "chi_sim", 
            "french": "fre", "german": "ger", "hebrew": "heb", 
            "italian": "ita", "russian": "rus", "spanish": "spa"}


def urllistfile(lang, n):
    return f"source-data/data_googlebooks-{langcode[lang]}-20200217/filelinklist_{n}grams.txt"

def totalcounts_1_file(lang):
    return f"source-data/data_googlebooks-{langcode[lang]}-20200217/totalcounts_1.txt"

def tmp_path(lang):

    path = f"ngrams/other/{lang}/tmp"

    if not os.path.exists(path):
        os.makedirs(path)

    return path


def per_gz_file_path(lang):

    path = f"ngrams/other/{lang}/most_freq_ngrams_per_gz_file"

    if not os.path.exists(path):
        os.makedirs(path)

    return path


###############################################################################
# Functions

def extract_ngram_sum_freq(line):
    """Extracts ngram and sum of frequencies across year_start to year_end
    from one line of a .gz file."""

    # split line by tab
    list_of_line_elements = line.strip().split('\t')

    # first element is always the ngram
    ngram = list_of_line_elements[0]

    # remainder is always a list with elements of form
    # "year,frequency,number_of_volumes"
    # sorted increasingly by year but with gaps
    year_freq = list_of_line_elements[1:]

    # omit some elements already before splitting to improve speed
    year_freq = year_freq[-max_relevant_year_freqs:]

    # split out year and frequency, filter, and sum freq

    freq = 0

    for yf in year_freq:

        yfs = yf.split(",")
        year_now = int(yfs[0])

        if year_now >= year_start & year_now <= year_end:

            freq += int(yfs[1])

    return ngram, freq


def get_most_freq_from_gz_file2(gz_file_url, lang, n):

    try:
        ngrams = list()
        freqs = list()

        gz_file_stream = urlopen(gz_file_url, timeout=60)

        with gzip.open(gz_file_stream, 'rt') as f:

            for line in f:

                ngram, freq = extract_ngram_sum_freq(line)

                # exclude ngrams not frequent enough
                if freq >= min_freq_to_keep[n]:
                    ngrams += [ngram]
                    freqs += [freq]

        # create dataframe, sort, and save to csv

        df = pd.DataFrame({'ngram': ngrams,
                           'freq': freqs})

        df = df.sort_values(by=['freq'], ascending=False)

        df.to_csv(f"{per_gz_file_path(lang)}/ngrams_"
                  f"{gz_file_url.split(sep='/')[-1]}.csv", index=False)

    except Exception as e:
        if continue_on_exception:
            print(f"ERROR: file {gz_file_url.split(sep='/')[-1]} not handled")
            print(e)
        else:
            raise e   # TODO doesn't work as expected



def get_most_freq_from_gz_file(gz_file_path, lang, n):
    """Get the most frequent ngrams from one .gz file and save as .csv file."""

    # read file line by line and collect lists of ngrams and frequencies

    ngrams = list()
    freqs = list()

    with gzip.open(gz_file_path, 'rt') as f:

        for line in f:

            ngram, freq = extract_ngram_sum_freq(line)

            # exclude ngrams not frequent enough
            if freq >= min_freq_to_keep[n]:
                ngrams += [ngram]
                freqs += [freq]

    # create dataframe, sort, and save to csv

    df = pd.DataFrame({'ngram': ngrams,
                       'freq': freqs})

    df = df.sort_values(by=['freq'], ascending=False)

    df.to_csv(f"{per_gz_file_path(lang)}/ngrams_"
              f"{gz_file_path.split(sep='/')[-1]}.csv", index=False)


def download_and_process_one_gz_file(gz_file_url, lang, n):
    """Download and process one .gz file."""

    # create out name and path from url
    gz_filename = gz_file_url.split(sep="/")[-1]
    gz_file_path = tmp_path(lang) + '/' + gz_filename

    # download .gz file
    print("downloading...")
    start = timer()
    wget.download(gz_file_url, gz_file_path)
    end = timer()
    print(f"download time: {round(end - start, 2)}s")

    # process the file
    print("processing...")
    start = timer()
    get_most_freq_from_gz_file(gz_file_path, lang, n)
    end = timer()
    print(f"processing time: {round(end - start, 2)}s")

    # remove file after to save space
    os.remove(gz_file_path)


def download_and_process_one_gz_file2(lang, n, urls, i):
    """Download and process one .gz file."""

    gz_file_url = urls[i]

    lenurls = len(urls)
    print(f"starting: lang={lang}, n={n}, file {i+1:0{len(str(lenurls))}} of {lenurls}")

    # create out name and path from url
    gz_filename = gz_file_url.split(sep="/")[-1]
    gz_file_path = tmp_path(lang) + '/' + gz_filename

    # download and process the file
    #print("processing...")
    start = timer()
    get_most_freq_from_gz_file2(gz_file_url, lang, n)
    end = timer()
    print(f"finished: lang={lang}, n={n}, file {i+1:0{len(str(lenurls))}} of {lenurls}: {round(end - start, 2)}s")
    #print(f"processing time: {round(end - start, 2)}s")

    # remove file after to save space
    #os.remove(gz_file_path)


def get_urls(lang, n):
    """Returns a list of urls from which we actually want to download a file."""

    urls = list()

    with open(urllistfile(lang, n)) as f:
        for line in f:
            urls += [line.strip()]

    if use_custom_url_indices:
        urls = [urls[i] for i in custom_url_indices[lang][n]]

    if not redownload_files:
        urls_already_downloaded = os.listdir(per_gz_file_path(lang))
        p = re.compile(f"^ngrams_{n}-.*\.gz\.csv")
        urls_already_downloaded = [s for s in urls_already_downloaded if p.match(s)]
        urls_short = ["ngrams_" + url.split("/")[-1] + ".csv" for url in urls]

        urls = [urls[i] for i in range(len(urls_short)) if urls_short[i] not in urls_already_downloaded]

    return urls


def download_and_process_each_gz_file():
    """Download and process each .gz file for each language in 'langs',
    and each n in 'ns' into raw, uncleaned .csv files of the most frequent n-grams."""

    for lang in langs:

        for n in ns:

            # Get list of urls of interest
            urls = get_urls(lang, n)

            # Loop across urls
            # TODO parallelize
            for i in range(len(urls)):
                print(f"\nlang={lang}, n={n}, file {i+1} of {len(urls)}:")
                download_and_process_one_gz_file2(lang, n, urls, i)


def download_and_process_each_gz_file_mp():
    """Download and process each .gz file for each language in 'langs',
    and each n in 'ns' into raw, uncleaned .csv files of the most frequent n-grams."""

    for lang in langs:

        for n in ns:

            # Get list of urls of interest
            urls = get_urls(lang, n)

            # Loop across urls
            if len(urls) > 0:

                if number_of_cores > 1:
                    pool = mp.Pool(number_of_cores)
                    func = partial(download_and_process_one_gz_file2, lang, n, urls)
                    pool.map(func, [i for i in range(len(urls))])
                    pool.close()
                    pool.join()

                else:
                    for i in range(len(urls)):
                        download_and_process_one_gz_file2(lang, n, urls, i)

        os.rmdir(tmp_path(lang))


###############################################################################
# run

if __name__ == '__main__':
    download_and_process_each_gz_file_mp()

