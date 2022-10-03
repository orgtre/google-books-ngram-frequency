# Creates source-data directory with links to source data
# run from repository root directory 'google-books-ngram-frequency'

import re, os, wget
import httplib2
from bs4 import BeautifulSoup, SoupStrainer


langcode = {"english": "eng", "english-us": "eng-us", "english-gb": "eng-gb",
            "english-fiction": "eng-fiction", "chinese_simplified": "chi_sim",
            "french": "fre", "german": "ger", "hebrew": "heb",
            "italian": "ita", "russian": "rus", "spanish": "spa"}

nmax = 5


def create_source_data_lists(langcode):
    """This function creates the directories "source-data/data_googlebooks-*"
    and fills them with files holding the urls of each gz file.
    For 1-grams, the totalcounts file is also added.
    Only needs to be run if Google changes the urls."""

    for n in range(1, nmax+1):

        for key, langc in langcode.items():
            
            if not os.path.exists(("source-data/data_googlebooks-"
                                   + f"{langc}-20200217/")):
                os.makedirs(("source-data/data_googlebooks-"
                             + f"{langc}-20200217/"))

            http = httplib2.Http()
            status, response = http.request(("http://storage.googleapis.com/"
                                             + "books/ngrams/books/20200217/"
                                             + f"{langc}/{langc}-{n}-"
                                             + "ngrams_exports.html"))

            urls = []
            for link in BeautifulSoup(response, parse_only=SoupStrainer('a')):

                if link.has_attr('href'):

                    if re.match(r".*gz$", link['href']):
                        urls += [link['href']]

                    elif (n == 1) & (re.match(r".*totalcounts-1$",
                                              link['href']) is not None):
                        filename = ("source-data/data_googlebooks-"
                                    + f"{langc}-20200217/totalcounts_1.txt")
                        
                        if os.path.exists(filename):
                            os.remove(filename)
                        
                        wget.download(link['href'], filename)

            with open((f"source-data/data_googlebooks-{langc}-"
                       + f"20200217/filelinklist_{n}grams.txt", 'w')) as f:

                for url in urls:
                    f.write("%s\n" % url)


if __name__ == '__main__':
    create_source_data_lists(langcode)
