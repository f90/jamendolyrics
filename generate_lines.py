# Creates line annotations in annotations/lines/*.csv from word annotations in
# annotations/words/*.csv.
import csv
import os

import glob

for fp in glob.glob(os.path.join("annotations", "words", "*.csv")):
    song_name = os.path.splitext(os.path.basename(fp))[0]

    # Read word timings
    with open(fp) as f:
        word_timings = list(csv.DictReader(f, delimiter=","))

    # Read word list
    word_list_path = os.path.join("lyrics", song_name + ".words.txt")
    if not os.path.exists(word_list_path):
        raise FileNotFoundError(
            f"Couldn't find word list file at {word_list_path}. Did you "
            "forget to generate it beforehand?"
        )
    with open(word_list_path) as f:
        words = f.read().splitlines()

    # Create line-by-line annotations
    assert len(word_timings) == len(
        words
    ), f"Found {len(word_timings)} timings in {fp} but {len(words)} words in {word_list_path}"
    annotations_by_line = []
    curr_line = {}
    for timing, word in zip(word_timings, words):
        # Potentially start new line
        if "start_time" not in curr_line.keys():
            assert len(curr_line.keys()) == 0
            curr_line["start_time"] = timing["word_start"]
        # Add current word to line text
        curr_line["lyrics_line"] = (
            word if "lyrics_line" not in curr_line.keys() else curr_line["lyrics_line"] + " " + word
        )
        # Potentially end current line
        if timing["line_end"] != "nan":
            curr_line["end_time"] = float(timing["line_end"])
            annotations_by_line.append(curr_line)
            curr_line = {}

    # Write to line CSV
    line_output_dir = os.path.join("annotations", "lines")
    os.makedirs(line_output_dir, exist_ok=True)
    line_output_path = os.path.join(line_output_dir, song_name + ".csv")
    with open(line_output_path, "w") as out_file:
        out_file.write("start_time,end_time,lyrics_line\n")
        for line in annotations_by_line:
            out_file.write(f"{str(line['start_time'])},{line['end_time']},{line['lyrics_line']}\n")

print("Finished converting annotations!")
