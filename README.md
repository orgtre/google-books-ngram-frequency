# Google Books n-gram frequency lists

*Note: Lists and code follow soon.*

This repository provides word and n-gram frequency lists for all the Google books corpora that can be searched with the [Google Books Ngram Viewer](https://books.google.com/ngrams/). The source data is version 20200217 of the n-gram lists made available by Google [here](https://storage.googleapis.com/books/ngrams/books/datasetsv3.html).

The full list of the corpora for which n-gram frequency lists are provided is: English, English Fiction, Chinese (simplified), French, German, Hebrew, Italian, Russian, and Spanish. In the provided lists the corpora are restricted to books published in the years 2010-2019.

Customizable Python code which reproduces the lists is also included.

The content of this repository is licensed under the [Creative Commons Attribution 3.0 Unported License](https://creativecommons.org/licenses/by/3.0/).


## Python code

Optionally, start by running `create_source_data_lists.py` from the repository root directory to recreate the `source-data` folder with lists of links to the Google source data files.

Run `download_and_extract_most_freq.py` to dowload each file listed in `source-data` (a ".gz-file") and extract the most frequent n-grams in it into a list saved in `ngrams/other/{lang}/most_freq_ngrams_per_gz_file`. To save computer resources each .gz-file is immediately deleted after this. Since the lists of most frequent n-grams per .gz-file still take up around 36GB with the standard settings, only one example list is uploaded to Github: `ngrams/other/english/most_freq_ngrams_per_gz_file/ngrams_1-00006-of-00024.gz.csv`. No cleaning has been performed at this stage, so this is how the raw data looks.

TODO upload code to gather lists of the most frequent n-grams across all .gz-files and clean them.
