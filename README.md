# Google Books n-gram frequency lists

This repository provides cleaned lists of the most frequent words and [n-grams](https://en.wikipedia.org/wiki/N-gram) (sequences of n words), including some English translations, of the [Google Books Ngram Corpus](#the-underlying-corpus) (v3/20200217, all languages), plus customizable [Python code](#python-code) which reproduces these lists.


## Lists with n-grams

Lists with the most frequent n-grams are provided separately by language and n. Available languages are Chinese (simplified), English, English Fiction, French, German, Hebrew, Italian, Russian, and Spanish. n ranges from 1 to 5. In the provided lists the language subcorpora are restricted to books published in the years 2010-2019, but in the Python code both this and the number of most frequent n-grams included can be adjusted.

The lists are found in the [ngrams](ngrams) directory. For all languages except Hebrew cleaned lists are provided for the

- 10.000 most frequent 1-grams, 
- 5.000 most frequent 2-grams, 
- 3.000 most frequent 3-grams, 
- 1.000 most frequent 4-grams,
- 1.000 most frequent 5-grams.

For Hebrew, due to the small corpus size, only the 200 most frequent 4-grams and 80 most frequent 5-grams are provided.

All cleaned lists also contain the number of times each n-gram occurs in the corpus (its frequency, column `freq`). For 1-grams (words) there are two additional columns: 

1. `cumshare` which for each word contains the cumulative share of all words in the corpus made up by that word and all more frequent words. 
2. `en` which contains the English translation of the word obtained using the [Google Cloud Translate API](https://cloud.google.com/translate) (only for non-English languages).

Here are the first 10 rows of [1grams_french.csv](ngrams/1grams_french.csv):
| ngram |       freq | cumshare | en     |
|:-----:|-----------:|---------:|:------:|
| de    | 1380202965 |    0.048 | of     |
| la    |  823756863 |    0.077 | the    |
| et    |  651571349 |    0.100 | and    |
| le    |  614855518 |    0.121 | the    |
| à     |  577644624 |    0.142 | at     |
| l'    |  527188618 |    0.160 | the    |
| les   |  503689143 |    0.178 | them   |
| en    |  390657918 |    0.191 | in     |
| des   |  384774428 |    0.205 | of the |

The lists found directly in the [ngrams](ngrams) directory have been cleaned and are intended for use when developing language-learning materials. The sub-directory [ngrams/more](ngrams/more) contains uncleaned and less cleaned versions which might be of use for e.g. linguists:

- the most frequent raw n-grams as Google stores them (suffixed `0_raw`),
- only keeping entries without part-of-speech (POS) tags (suffixed `1a_no_pos`),
- only keeping entries with POS tags (only for 1-grams, suffixed `1b_with_pos`),
- entries excluded from the final cleaned lists (suffixed `2_removed`).


## Learning languages with this

To provide some motivation for why leaning the most frequent words first may be a good idea when learning a language, the following graph is provided.
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="graph_1grams_cumshare_rank_dark.svg" width="100%">
  <source media="(prefers-color-scheme: light)" srcset="graph_1grams_cumshare_rank_light.svg" width="100%">
  <img alt="graph_1grams_cumshare_rank_*.svg" src="graph_1grams_cumshare_rank_light.svg" width="100%">
</picture>

For each language, it plots the frequency rank of each 1-gram (i.e. word) on the x-axis and the `cumshare` on the y-axis. So, for example, after learning the 1000 most frequent French words, one can understand more than 70% of all words, counted with duplicates, occurring in a typical book published between 2010 and 2019 in version 20200217 of the French Google Books Ngram Corpus.

For n-grams other than 1-grams the returns to learning the most frequent ones are not as steep, as there are so many possible combinations of words. Still, people tend to learn better when learning things in context, so one use of them could be to find common example phrases for each 1-gram. Another approach is the following: Say one wants to learn the 1000 most common words in some language. Then one could, for example, create a minimal list of the most common 4-grams which include these 1000 words and learn it.

Although the n-gram lists have been cleaned with language learning in mind and contain some English translations, they are not intended to be used directly for learning, but rather as intermediate resources for developing language learning materials. The provided translations only give the English word closest to the most common meaning of the word. Moreover, depending on ones language learning goals, the Google Books Ngram Corpus might not be the best corpus to base learning materials on – see the next section.


## The underlying corpus

This repository is based on the Google Books Ngram Corpus Version 3 (with version identifier 20200217), made available by Google as n-gram lists [here](https://storage.googleapis.com/books/ngrams/books/datasetsv3.html). This is also the data that underlies the [Google Books Ngram Viewer](https://books.google.com/ngrams/). The corpus is a subset, selected by Google based on the quality of optical character recognition and metadata, of the books digitized by Google and contains around 6% of all books ever published ([1](https://doi.org/10.1126/science.1199644), [2](https://dl.acm.org/doi/abs/10.5555/2390470.2390499), [3](https://doi.org/10.1371%2Fjournal.pone.0137041)).

When assessing the quality of a corpus, both its size and its representativeness of the kind of material one is interested in are important. 


### Size

The Google Books Ngram Corpus Version 3 is huge, as this table of the count of words in it by language and subcorpus illustrates:

| Language         | # words, all years | # words, 2010-2019 |
|------------------|-------------------:|-------------------:|
| Chinese          |     10,778,094,737 |        257,989,144 |
| English          |  1,997,515,570,677 |    283,795,232,871 |
| American English |  1,167,153,993,435 |    103,514,367,264 |
| British English  |    336,950,312,247 |     45,271,592,771 |
| English Fiction  |    158,981,617,587 |     73,746,188,539 |
| French           |    328,796,168,553 |     35,216,041,238 |
| German           |    286,463,423,242 |     57,039,530,618 |
| Hebrew           |      7,263,771,123 |         76,953,586 |
| Italian          |    120,410,089,963 |     15,473,063,630 |
| Russian          |     89,415,200,246 |     19,648,780,340 |
| Spanish          |    158,874,356,254 |     17,573,531,785 |

Note that these numbers are for the total number of words, not the number of unique words. They also include many words which aren't valid words, but due to the size of the corpus, the cleaning steps are performed on only the most common words, so the number of words that would remain in the whole corpus after cleaning is unavailable. Moreover, Google uploads only words that appear over 40 times, while these counts also include words appearing less often than that.

We see that even after restricting the language subcorpora to books published in the last 10 available years, the number of words is still larger than 15 billion for each subcorpus, except Chinese and Hebrew. This is substantially larger than for all other corpora in common use, which never seem to contain more than a few billion words and often are much smaller than that ([4](https://en.wikipedia.org/wiki/List_of_text_corpora)).


### Representativeness 

When it comes to representativeness, it depends on the intended use. The Google Books Ngram Corpus contains only books (no periodicals, spoken language, websites, etc.). Each book edition is included at most once. Most of these books come from a small number of large university libraries, "over 40" in Version 1 of the corpus, while a smaller share is obtained directly from publishers ([1](https://doi.org/10.1126/science.1199644)). So, for example, if one intends to use this corpus for learning a language in which one mainly will read books of the kind large university libraries are interested in, then the words in this corpus are likely to be quite representative of the population of words one might encounter in the future.


## Python code

The code producing everything is in the [python](python) directory. Each .py-file is a script that can be run from the command-line using `python python/filename`, where the working directory has to be the directory containing the python directory. Every .py-file has a settings section at the top and additional cleaning settings can be specified using the files in [python/extra_settings](python/extra_settings). The default settings have been chosen to make the code run reasonably fast and keep the resulting repository size reasonably small.


### Reproducing everything

Optionally, start by running [create_source_data_lists.py](python/create_source_data_lists.py) from the repository root directory to recreate the [source-data](source-data) folder with lists of links to the Google source data files.

Run [download_and_extract_most_freq.py](python/download_and_extract_most_freq.py) from the repository root directory to download each file listed in [source-data](source-data) (a ".gz-file") and extract the most frequent n-grams in it into a list saved in `ngrams/more/{lang}/most_freq_ngrams_per_gz_file`. To save computer resources each .gz-file is immediately deleted after this. Since the lists of most frequent n-grams per .gz-file still take up around 36GB with the default settings, only one example list is uploaded to GitHub: [ngrams_1-00006-of-00024.gz.csv](ngrams/more/english/most_freq_ngrams_per_gz_file/ngrams_1-00006-of-00024.gz.csv). No cleaning has been performed at this stage, so this is how the raw data looks.

Run [gather_and_clean.py](python/gather_and_clean.py) to gather all the n-grams into lists of the overall most frequent ones and clean these lists (see the next section for details).

Run [google_cloud_translate.py](python/google_cloud_translate.py) to add English translations to all non-English 1-grams using the [Google Cloud Translate API](https://cloud.google.com/translate) (this requires an API key, see the file header). By default only 1-grams are translated and only to English, but by changing the settings any n-gram can be translated to any language supported by Google. Google randomly capitalizes translations so an attempt is made to correct for this. Moreover, a limited number of manual corrections are applied using [manual_translations_1grams.csv](python/extra_settings/manual_translations_1grams.csv).

Finally, [graph_1grams_cumshare_rank.py](python/graph_1grams_cumshare_rank.py) produces [graph_1grams_cumshare_rank_light.svg](graph_1grams_cumshare_rank_light.svg) and its dark version.


### Cleaning steps performed

All the cleaning steps are performed in [gather_and_clean.py](python/gather_and_clean.py), except the cleaning of the Google translations.

The following cleaning steps are performed programmatically: 

1. part-of-speech (POS) tags are removed
2. _1-grams, French and Italian_: contractions are split
3. trailing "_" is removed
4. capitalized and uncapitalized n-grams are merged
5. n-grams consisting of only punctuation and/or numbers are removed
6. _1-grams, German_: words containing only uppercase letters are removed unless in the manually created list of exceptions [upcases_to_keep.csv](python/extra_settings/upcases_to_keep.csv)
7. _1-grams, except German_: words starting with an uppercase letter are removed unless in the manually created lists of exceptions [upcases_to_keep.csv](python/extra_settings/upcases_to_keep.csv)
8. _1-grams_: one-character words are removed unless in the manually created lists of exceptions [onechars_to_keep.csv](python/extra_settings/onechars_to_keep.csv)
9. _German and Russian_: contractions are removed
10. _English fiction_: remove n-gram if starting with `"'"`
11. n-grams with non-word characters other than `"'"`, `" "`, and `","` are removed
	- additionally other than `"-"` for Russian and `"\""` for Hebrew
12. n-grams with numbers are removed
13. n-grams in the wrong alphabet are removed.

Moreover, the following cleaning steps have been performed manually, using the English translations to help inform decisions: 

14. _1-grams, all languages_: The lists of removed words have been checked for words wrongly removed.
15. _1-grams, except Hebrew_: The cleaned lists have been fully checked for extra words to exclude. 
16. _1-grams, Hebrew_: The cleaned lists have been checked for extra words to exclude up to rank 100.
17. When n-grams wrongly included or excluded were found during the manual cleaning steps above, this was corrected for by either adjusting the programmatic rules, or by adding them to one of the lists of exceptions, or by adding them to the final lists of extra n-grams to exclude.
18. n-grams in the manually created lists of extra n-grams to exclude have been removed. These lists are in [python/extra_settings](python/extra_settings) and named `extra_{n}grams_to_exclude.csv`.

When manually deciding which words to include and exclude the following rules were applied. _Exclude_: person names (some exceptions: Jesus, God), city names (some exceptions: if differ a lot from English and are common enough), company names, abbreviations (some exceptions, e.g. ma, pa), word parts, words in the wrong language (except if in common use). _Do not exclude_: country names, names for ethnic/national groups of people, geographical names (e.g. rivers, oceans), colloquial terms, interjections.


## Related work

For a carefully created list of all words in the English part of the Google Books Ngram Corpus (version 20200217), sorted by frequency, see the [hackerb9/gwordlist](https://github.com/hackerb9/gwordlist) repository.

An extensive list of frequency lists in many languages is available on [Wiktionary](https://en.wiktionary.org/wiki/Wiktionary:Frequency_lists).


## Limitations and known problems

What remains to be done is completing the final manual cleaning for Hebrew and the cleaning of the lists of n-grams for n > 1. An issue that might be addressed in the future is that some of the latter contain "," as a word. It might also be desirable to include more common abbreviations. No separate n-gram lists are provided for the American English and British English corpora. Of course, some errors remain. 

The content of this repository is licensed under the [Creative Commons Attribution 3.0 Unported License](https://creativecommons.org/licenses/by/3.0/). Issue reports and pull requests are most welcome!
