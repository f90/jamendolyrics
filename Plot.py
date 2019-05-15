from configparser import ConfigParser

import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from Evaluate import read_predictions

def lognorm(x):
    logs = np.log10(np.abs(x) + 1)
    logs[x < 0.0] *= -1
    return logs

def denorm(x):
    exps = np.power(10.0, np.abs(x)) - 1
    exps[x < 0.0] *= -1
    return exps

def plot_error_histogram(deviations_dicts, save_path=None):
    if not isinstance(deviations_dicts[0], dict):
        fig, ax = plt.subplots(figsize=(20, 10))

        for idx, l in enumerate(deviations_dicts):
            sns.kdeplot(lognorm(l), ax=ax, gridsize=500)

        tick_pos_names = np.array([-40, -20, -10, -5, -1, -0.5, -0.2, 0, 0.2, 0.5, 1, 5, 10, 20, 40])
        tick_pos_log = lognorm(tick_pos_names)
        ax.set_xticks(tick_pos_log)
        ax.set_xticklabels(tick_pos_names)

        plt.title("Histogram of errors (s)")
        plt.xlabel("Predicted start time - actual start time (s)")
        plt.ylabel("Frequency")

        if save_path != None:
            plt.savefig(save_path)
        plt.close()
    else:
        raise NotImplementedError

def plot_error_over_time(deviations_dict, ref_dict, total_durations, save_path=None):
    f, axes = plt.subplots(len(total_durations)//2, 2, sharex=True, sharey=True, figsize=(10,20))
    for idx, song in enumerate(total_durations.keys()):
        # Collect data from all approaches
        x = ref_dict[song]
        ax = axes[idx//2][idx%2]

        ax.axhline(0, ls='--', color="black")
        ax.set_title(song)
        for approach_dict in deviations_dict:
            # Normalize deviations
            ax.plot(x, lognorm(approach_dict[song]), "o-", markersize=1, linewidth=1)

    tick_pos_names = np.array([-40, -10, -2, 0, 2, 10, 40])
    tick_pos_log = lognorm(tick_pos_names)
    axes[0][0].set_yticks(tick_pos_log)
    axes[0][0].set_yticklabels(tick_pos_names)

    if save_path != None:
        plt.savefig(save_path)

    plt.close()

def plot_deviations():
    preds = list()

    # Jamendo dataset
    config = ConfigParser(inline_comment_prefixes=["#"])
    config.read("conf/stoller.cfg")
    preds.append(read_predictions(config))

    # Jamendo dataset, source sep variant
    config = ConfigParser(inline_comment_prefixes=["#"])
    config.read("conf/stoller_source_sep.cfg")
    preds.append(read_predictions(config))

    ### ADD YOUR OWN MODEL HERE ###

    # Plot error histogram
    plot_error_histogram([p["all_deviations"] for p in preds], "plots/jamendo_histogram.png")

    # Plot errors over time
    plot_error_over_time([p["deviations_dict"] for p in preds], preds[-1]["ref_dict"], preds[-1]["total_durations"],
                         "plots/jamendo_error_over_time.png")


plot_deviations()