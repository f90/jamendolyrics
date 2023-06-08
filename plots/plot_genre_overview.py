"""
Plots a pie-chart showing an overview of the genre distribution in the dataset
"""

import csv
import random

import matplotlib.pyplot as plt
import seaborn as sns

# Go through metadata CSV and read genre attribute
with open("../JamendoLyrics.csv", "r") as f:
    rows = csv.DictReader(f)
    genres = [row["Genre"] for row in rows]
    unique_genres = list(set(genres))
    genre_freq = [len([g for g in genres if g == target]) for target in unique_genres]

# define Seaborn color palette to use
colors = sns.color_palette("Set3")
random.shuffle(colors)

plt.rcParams["font.family"] = "serif"
plt.rcParams["font.serif"] = ["Times New Roman"]
plt.rcParams["font.size"] = 14

# Create pie chart
plt.pie(
    genre_freq,
    labels=unique_genres,
    radius=1,
    wedgeprops=dict(width=0.3, edgecolor="w"),
    colors=colors,
)
plt.savefig("genre_distribution.pdf", bbox_inches="tight")
