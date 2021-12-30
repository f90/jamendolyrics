# Jamendo lyrics database for lyrics alignment and transcription evaluation

This repository is released alongside the paper

[End-to-end Lyrics Alignment for Polyphonic Music Using an Audio-to-Character Recognition Model](https://arxiv.org/abs/1902.06797)

It contains 

* 20 music pieces under CC license from the Jamendo website along with their lyrics, with...
  * Manual annotations indicating the start time of each word in the audio file
  * Predictions of start and end times for each word from both of the models presented in the [paper](https://arxiv.org/abs/1902.06797)
* Code for evaluating lyrics alignment models using this database with multiple metrics
* Code for visualising the overall model accuracy as well as accuracy for each song and word

These resources allow the evaluation of lyrics alignment (and lyrics transcription) models on a dataset with diverse genres.

## Installation

Requirements are Python 3 with packages installed as listed in ``requirements.txt.``

## Evaluating lyrics alignment performance

Lyrics alignment models can be evaluated with our Evaluate.py function according to the following metrics:

* For the deviation between correct and predicted start times:
  * Mean
  * Median
* For the absolute errors (AE):
  * Mean AE, averaged over songs (as used in [MIREX 2017](https://www.music-ir.org/mirex/wiki/2017:Automatic_Lyrics-to-Audio_Alignment))
  * Mean AE, median over songs
  * Median AE, averaged over songs
  * Median AE, median over songs
  * Mean AE, standard deviation over songs
* Percentage of correct segments (Perc) metric, averaged over songs
* [Mauch metric](https://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.310.799) (with different tolerance values)
* [Perceptually weighted synchronicity score](https://zenodo.org/record/5625688) (thanks to Ninon Lizé Masclef and Manuel Moussallam for the implementation)

### Reproducing the paper results

To evaluate the models from the paper and reproduce the paper's results, simply run 

```
python Evaluate.py
```

and you will see a list of all performance metrics for both models.

### Evaluating your own models

To evaluate your own model's predictions, save them as a separate folder in the subfolder predictions. The format needs to be the same as for the models from the paper (see these files for comparison). Specifically, we expect one CSV file for each song with the name ``<AUDIO_FILE_NAME>_align.csv``.
Each row should correspond to one word of the lyrics, as given in the file ``<AUDIO_FILE_NAME>.words.txt`` in the ``lyrics`` subfolder, and should give the predicted start time and end time in seconds of that word, separated by a comma.

Then, create a configuration file in the conf subfolder (again see the configuration files for our models for guidance on this).

Finally, modify the ``main()`` function in ``Evaluate.py`` by adding

```
config = ConfigParser(inline_comment_prefixes=["#"])
config.read("conf/YOUR_CONFIG_NAME.cfg")
results = compute_metrics(config)
print_results(results)
```

under the line saying ``### ADD YOUR OWN MODEL HERE ###``, where ``YOUR_CONFIG_NAME`` is the name of your config file that is used to find your predictions.
Then you can run ``Evaluate.py`` to get your model evaluation results, alongside the models from the paper.

## Visualising model predictions

``Plot.py`` contains some rudimentary plotting functionality to visualise the overall accuracy of models as well as what mistakes they make in each song at each point in time.

The resulting plots for our model are contained in the subfolder ``plots``.
``jamendo_histogram.png`` shows the histogram of errors for our model (blue) and source separated variant (orange).
``jamendo_error_over_time.png`` shows the deviation of these models for each song at the beginning of each word. Negative values indicate a word has been predicted too early, positive that it's too late.

To generate these plots for your own model, first integrate the predictions following the "Evaluating your own models" section above.
Then, in ``Plot.py``, add the following code snippet to the ``plot_deviations`` function under the line ``### ADD YOUR OWN MODEL HERE ###``:

    config = ConfigParser(inline_comment_prefixes=["#"])
    config.read("conf/YOUR_CONFIG_NAME.cfg")
    preds.append(read_predictions(config))
    
where ``YOUR_CONFIG_NAME`` is the name fo your configuration file. 
Then run ``Plot.py``, and your model performance should then be visualised alongside the models from the paper, and saved in the plots subfolder.
