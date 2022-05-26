from __future__ import division
from configparser import ConfigParser

import numpy as np
import glob
import os
import csv
import librosa
from scipy.stats import skewnorm


def mauch_correct(ref_timestamps, pred_timestamps, tolerance):
    # For given reference and prediction timestamps and a tolerance threshold, compute the metric defined in Mauch et al
    assert len(ref_timestamps) == len(pred_timestamps)
    deviations = np.abs(ref_timestamps - pred_timestamps)
    return np.mean(deviations < tolerance)


def duration_correct(ref_timestamps, pred_timestamps, total_duration):
    # Compute for given ref and prediction timestamps and the total song duration,
    # what percentage of time the predicted position coincides with the true position (between 0 and 1)
    assert len(ref_timestamps) == len(pred_timestamps)
    assert (
        np.max(ref_timestamps) <= total_duration
        and np.max(pred_timestamps) <= total_duration
    )
    correct = 0.0
    ref_prev = 0.0
    pred_prev = 0.0
    for i in range(len(ref_timestamps)):
        # Compare intersection of intervals [ref_prev, ref_curr] and [pred_prev, pred_curr]
        corr_interval_start = max(ref_prev, pred_prev)
        corr_interval_end = min(ref_timestamps[i], pred_timestamps[i])
        correct += max(corr_interval_end - corr_interval_start, 0)

        ref_prev = ref_timestamps[i]
        pred_prev = pred_timestamps[i]
    # One last calculation for final interval until end of track
    corr_interval_start = max(ref_prev, pred_prev)
    corr_interval_end = total_duration
    correct += max(corr_interval_end - corr_interval_start, 0)

    percentage_correct = correct / total_duration
    return percentage_correct


def mauch_metric(ref_dict, pred_dict, threshold):
    # Compute metric defined in Mauch et al
    mauch_percentages = [
        mauch_correct(ref_dict[key], pred_dict[key], threshold) for key in ref_dict
    ]
    return np.mean(mauch_percentages)


def perc_metric(ref_dict, pred_dict, total_durations):
    # Percentage of correct segments (Perc) metric
    correct_percentages = [
        duration_correct(ref_dict[key], pred_dict[key], total_durations[key])
        for key in ref_dict
    ]
    return np.mean(correct_percentages)


def perceptual_synchrony(offset):
    """function perceptually weighting the deviations of onsets"""
    skewness = 1.12244251
    localisation = -0.22270315
    scale = 0.29779424
    normalisation_factor = 1.6857
    return (1.0 / normalisation_factor) * skewnorm.pdf(
        offset, skewness, loc=localisation, scale=scale
    )


def perceptual_metric(ref_dict, pred_dict):
    """metric based on human synchronicity perception as measured in the paper

    "User-centered evaluation of lyrics to audio alignment", N. Lizé-Masclef, A. Vaglio, M. Moussallam, ISMIR 2021

    The parameters of this function were tuned on data collected through a user Karaoke-like experiment
    It reflects human judgment of how "synchronous" lyrics and audio stimuli are perceived in that setup.

    Beware that this metric is non-symmetrical, assuming the `ref_dict` argument is the ground truth for words actual position in the audio signal.
    By construct, it is also not equal to 1 at 0.
    """
    perceptual_score = [
        perceptual_synchrony(pred_dict[key] - ref_dict[key]) for key in ref_dict
    ]
    return np.mean([np.mean(ppe) for ppe in perceptual_score])


def read_predictions(cfg):
    label_paths = glob.glob(
        os.path.join(cfg.get("main", "LABEL_PATH"), "*" + cfg.get("main", "LABEL_EXT"))
    )

    pred_dict = dict()
    ref_dict = dict()
    deviations_dict = dict()
    total_durations = dict()

    print("Found " + str(len(label_paths)) + " annotated songs. Reading annotations...")

    for label in label_paths:
        with open(label) as f:
            rows = list(csv.DictReader(f, delimiter=","))
        label_filename = os.path.split(label)[1]
        prediction_filename = label_filename.replace(
            cfg.get("main", "LABEL_EXT"), cfg.get("main", "PREDICTION_EXT")
        )
        prediction = os.path.join(
            cfg.get("main", "PREDICTION_PATH"), prediction_filename
        )
        audio_filename = label_filename.replace(cfg.get("main", "LABEL_EXT"), ".mp3")
        audio, sr = librosa.load(
            os.path.join(cfg.get("main", "MP3_PATH"), audio_filename),
            sr=None,
            mono=True,
        )
        total_durations[label_filename] = float(len(audio)) / float(sr)

        # Get predictions
        with open(prediction) as f:
            pred_rows = list(
                csv.reader(f, delimiter=str(cfg.get("main", "PREDICTION_DELIM")))
            )
        assert len(pred_rows) == len(rows)

        # Take start times and convert to numpy arrays
        pred_times = np.array([float(row[0]) for row in pred_rows])
        ref_times = np.array([float(row["word_start"]) for row in rows])

        # Apply delay to predictions
        pred_times += float(cfg.get("main", "DELAY"))
        if np.min(pred_times) < 0:
            print(
                "WARNING: When applying delay to predictions in " + str(label),
                " got negative time! Setting to 0!",
            )
            pred_times = np.maximum(pred_times, 0)

        # Save reference and prediction
        pred_dict[label_filename] = pred_times
        ref_dict[label_filename] = ref_times

        # Compute and save deviations
        deviations_dict[label_filename] = pred_times - ref_times

    # All predictions in one list
    all_deviations = list()
    for val in deviations_dict.values():
        all_deviations.extend(val)
    all_deviations = np.array(all_deviations)

    return {
        "ref_dict": ref_dict,
        "pred_dict": pred_dict,
        "deviations_dict": deviations_dict,
        "total_durations": total_durations,
        "all_deviations": all_deviations,
    }


def print_results(results_dict):
    print("RESULTS: ")
    for val in results_dict.values():
        print(val[1] + ": " + str(val[0]))
    print("-------------------------")


def compute_metrics(config):
    results = dict()
    # Read data
    preds = read_predictions(config)

    print("EVALUATING " + str(len(preds["deviations_dict"])) + " songs...")

    results["mean_deviation"] = (np.mean(preds["all_deviations"]), "Mean error")
    results["median_deviation"] = (np.median(preds["all_deviations"]), "Median error")
    results["mean_AE"] = (
        np.mean([np.mean(np.abs(val)) for val in preds["deviations_dict"].values()]),
        "Mean absolute error, averaged over all songs",
    )

    results["mean_AE_median_avg"] = (
        np.median([np.mean(np.abs(val)) for val in preds["deviations_dict"].values()]),
        "Mean absolute error, medianed over all songs",
    )

    results["median_AE"] = (
        np.mean([np.median(np.abs(val)) for val in preds["deviations_dict"].values()]),
        "Median absolute error, averaged over all songs",
    )

    results["median_AE_median_avg"] = (
        np.median(
            [np.median(np.abs(val)) for val in preds["deviations_dict"].values()]
        ),
        "Median absolute error, medianed over all songs",
    )

    results["mean_AE_std"] = (
        np.std([np.mean(np.abs(val)) for val in preds["deviations_dict"].values()]),
        "Mean absolute error, standard deviation over all songs",
    )

    results["mean_perc"] = (
        perc_metric(preds["ref_dict"], preds["pred_dict"], preds["total_durations"]),
        "Perc: Mean proportion of correct annotation, averaged over songs",
    )

    results["mean_perceptual"] = (
        perceptual_metric(preds["ref_dict"], preds["pred_dict"]),
        "Perceptual: Perceptually weighted synchronicity score, averaged over songs",
    )

    for tolerance in np.linspace(0.1, 1.0, 10):
        results["mauch_" + str(tolerance)] = (
            mauch_metric(preds["ref_dict"], preds["pred_dict"], tolerance),
            "Mauch metric, threshold of " + str(tolerance) + " seconds",
        )

    return results


def main():
    print("EVALUATING on Jamendo dataset, evaluate model from Stoller et al...")
    config = ConfigParser(inline_comment_prefixes=["#"])
    config.read("conf/stoller.cfg")
    results = compute_metrics(config)
    print_results(results)

    print(
        "EVALUATING on Jamendo dataset, evaluate model from Stoller at al, source separated version..."
    )
    config = ConfigParser(inline_comment_prefixes=["#"])
    config.read("conf/stoller_source_sep.cfg")
    results = compute_metrics(config)
    print_results(results)

    ### ADD YOUR OWN MODEL HERE ###


if __name__ == "__main__":
    main()
