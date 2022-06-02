# This script generates line-level annotation in the form of CSVs (see example below) - based on
# the line_end entry in the word annotations, it detects the endings of lines and their end
# positions. Basically the information is only converted to a format that might be easier to read
# for some purposes (e.g. line-level training/test data creation).

# CSV structure:
# (start_time, end_time, lyrics_line)
# 0.5, 1.3, Hey you
# 1.5, 1.8, I am listening
# ...
import csv
import glob
import os
import math

for annotation_path in glob.glob(os.path.join("annotations/words", "*.csv")):
    out_dir = os.path.join("annotations", "lines")
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    out_path = os.path.join(out_dir, os.path.basename(annotation_path))
    with open(annotation_path) as f:
        annotation = list(csv.DictReader(f, delimiter=","))
    with open(
        os.path.join(
            "lyrics", os.path.basename(annotation_path).replace(".csv", ".words.txt")
        )
    ) as f:
        words = f.read().splitlines()

    with open(out_path, "w") as out_file:
        out_file.write("start_time,end_time,lyrics_line\n")
        curr_line = ""
        line_start = None
        for word_idx, (word, time) in enumerate(zip(words, annotation)):
            curr_line += word + " "
            if line_start is None:
                # Starting a new line - set line start to the start of the word
                line_start = float(time["word_start"])

            if not math.isnan(float(time["line_end"])):
                # A line ends here - write it, using the line_end column
                line_end = float(time["line_end"])
                assert line_end > line_start, (
                    f"Found line in {annotation_path} with line end "
                    f"{line_end} before line start {line_start}!"
                )
                out_file.write(f"{str(line_start)},{line_end},{curr_line.strip()}\n")

                curr_line = ""
                line_start = None

        assert (
            line_start is None
        ), f"Last word in annotation did NOT end a lyrical line!"

print("Line annotation successfully generated at 'annotations/lines/*.csv'!")
