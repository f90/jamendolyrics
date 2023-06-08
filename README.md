# JamendoLyrics MultiLang dataset for lyrics research

A dataset containing 80 songs with different genres and languages along with lyrics that 
are time-aligned on a word-by-word level (with start and end times) to the music.

To cite this dataset and for more information, please refer to the following paper, where this 
dataset was first used:

[Similarity-based Audio-Lyrics Alignment of Multiple Languages
](https://ieeexplore.ieee.org/document/10096725)
\
ICASSP 2023
\
Simon Durand, Daniel Stoller, Sebastian Ewert

## Installation

The dataset can be used without installation by cloning it from this Github repository. 

For running any of the included scripts, we require Python 3.10 with packages installed as 
listed in ``requirements.txt.``

## Metadata CSV

All songs are listed in `JamendoLyrics.csv` together with their metadata.
To load annotations you are interested in, you can iterate over this CSV and use the `Filepath` 
column to build file paths to files containing the data for each song (audio file, lyrics 
annotations). Among the metadata, "LyricOverlap" refers to whether or not the lyrics in the song overlap,
“Polyphonic” refers to whether or not there are multiple singers singing the same lyrics, but with different melodies,
and "NonLexical" refers to whether or not there is non-lexical singing (eg: scatting).

## Lyrics files

In the `lyrics` subfolder, we provide the lyrics to each song as `SONG_NAME.txt` (normalized, e.
g. special characters and characters not supported in `vocab/international.characters` are removed)

Furthermore, `SONG_NAME.words.txt` contains all the words, separated by 
lines, ignoring the paragraph structure of the original lyrics. This is used for the word-level timestamp annotations.

## Time-aligned lyrics annotations

We have aligned the lyrics on a word-by-word and line-by-line basis to the music.

Word-by-word start and end timestamps are stored in the "annotations/words" subfolder, and they 
also indicate whether the word represents the end of a line as well (it will have the word end 
timestamp set instead of NaN).

A line-by-line version of the lyrics is stored in the subfolder
"annotations/lines" as CSV files, denoting the start and end time of each lyrical line in the audio.
These contain one row per line in the form of `(start_time, end_time, lyrics_line)` and can be
used to train or evaluate models only on a line-by-line level.

### Modifying word-by-word timestamps

In case the word timestamps are modified, one needs to run `generate_lines.py` to 
update the line-level timestamp files in "annotations/lines" accordingly. 

This is because the line-level annotation in "annotations/lines" is auto-generated based on the manual
word-by-word annotations: The start timestamp for each line is set to be the start timestamp of the 
word after an end-of-line word.

In case you find errors in the timestamp annotations, we encourage you to submit a pull request 
to this repository so we can correct the errors.

## Acknowledgements

We want to acknowledge our 2022 Research intern, [Emir Demirel](https://emirdemirel.github.io/), 
and Torr Yatco for their help in assembling this dataset.

## Original dataset

This dataset is an extended version of the original JamendoLyrics dataset presented in the paper

[End-to-end Lyrics Alignment for Polyphonic Music Using an Audio-to-Character Recognition Model](https://arxiv.org/abs/1902.06797)

It originally contained only 20 English songs and is now deprecated as annotations are slightly improved, 
so we discourage its use in the future.
You can find it archived [here](https://github.com/f90/jamendolyrics/releases/tag/original).
