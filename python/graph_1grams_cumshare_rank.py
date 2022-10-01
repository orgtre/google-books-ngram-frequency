# Create a graph of cumshare vs rank for 1-grams across languages

import pandas as pd
import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter, PercentFormatter


###############################################################################
# Settings

langs = ["chinese_simplified", "english", "french", "german", "hebrew",
         "italian", "russian", "spanish"]
langnames = ["Chinese", "English", "French", "German", "Hebrew",
             "Italian", "Russian", "Spanish"]


###############################################################################
# Functions

def get_fig(use_dark):
    
    d = pd.DataFrame()
    for lang in langs:
        d[lang] = pd.read_csv(f"ngrams/1grams_{lang}.csv",
                              usecols=['cumshare'], nrows=10000)

    d.index = range(1, len(d)+1)
    d.columns = langnames

    plt.clf()
    matplotlib.rcParams.update(matplotlib.rcParamsDefault)
    sns.set_theme(style="whitegrid")
    plt.rcParams.update({"grid.linewidth":0.5, "grid.alpha":0.6})
    
    if use_dark:
        plt.style.use("dark_background")
        light_or_dark = "dark"
    else:
        light_or_dark = "light"
        
    plot = sns.lineplot(data=d, palette="tab10", linewidth=1)
    plot.legend(bbox_to_anchor=(0.001, 1.0), loc="upper left")
    plot.set_xlabel("Most common words learned")
    plot.set_ylabel("% words in a typical book one can understand")
    plot.set(xscale="log")
    plot.get_xaxis().set_major_formatter(ScalarFormatter())
    plot.get_yaxis().set_major_formatter(PercentFormatter(xmax=1.0, symbol=''))
    plt.xlim(1, 10000)
    plt.ylim(0, 1)
    plt.savefig(f"graph_1grams_cumshare_rank_{light_or_dark}.svg")

    
###############################################################################
# Run
    
if __name__ == '__main__':
    get_fig(False)
    get_fig(True)
