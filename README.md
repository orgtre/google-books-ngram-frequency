# Google Books n-gram frequency lists

This repository provides word and n-gram frequency lists for all the Google books corpora that can be searched with the [Google Books Ngram Viewer](https://books.google.com/ngrams/). The source data is version 20200217 of the n-gram lists made available by Google [here](https://storage.googleapis.com/books/ngrams/books/datasetsv3.html).

The full list of the corpora for which n-gram frequency lists are provided is: English, English Fiction, Chinese (simplified), French, German, Hebrew, Italian, Russian, and Spanish. In the provided lists the corpora are restricted to books published in the years 2010-2019.

Customizable Python code which reproduces the lists is also included.

The content of this repository is licensed under the [Creative Commons Attribution 3.0 Unported License](https://creativecommons.org/licenses/by/3.0/).


## Lists with n-grams

The lists with the most frequent n-grams for each language and n from 1 to 5 are found in the `ngrams` directory. The lenght of these lists varies with n and language; for example, the 10.000 most common words (1-grams) are provided for each language.

The lists found directly in the `ngrams` directory have been cleaned and are intended for use when developing language-learning materials. The sub-directory `ngrams/more` contains uncleaned and less cleaned versions which might be of use for e.g. linguists. The lists suffixed "removed" can be used to check what words are excluded from the final cleaned lists.


## Python code

Optionally, start by running `create_source_data_lists.py` from the repository root directory to recreate the `source-data` folder with lists of links to the Google source data files.

Run `download_and_extract_most_freq.py` from the repository root directory to dowload each file listed in `source-data` (a ".gz-file") and extract the most frequent n-grams in it into a list saved in `ngrams/more/{lang}/most_freq_ngrams_per_gz_file`. To save computer resources each .gz-file is immediately deleted after this. Since the lists of most frequent n-grams per .gz-file still take up around 36GB with the default settings, only one example list is uploaded to Github: `ngrams/more/english/most_freq_ngrams_per_gz_file/ngrams_1-00006-of-00024.gz.csv`. No cleaning has been performed at this stage, so this is how the raw data looks.

Run `gather_and_clean.py`to gather all the n-grams into lists of the overall most frequent ones and clean these lists by excluding unwanted n-grams.


## Limitations and known problems

The n-gram lists still contain entries which should be excluded, and, especially for n larger than one, some n-grams have been wrongfully excluded. Hence the lists are still subject to change. Version tags will be introduced once they are somewhat stable.

