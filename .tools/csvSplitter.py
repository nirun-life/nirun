# Original Author Ramesh Nelluri
# https://python.plainenglish.io/split-a-large-csv-file-randomly-or-equally-into-smaller-files-76f7bb734459
#
# Modified by Piruin Panichphol
#
# Update
# - write header to each split file

import logging
import random

import pandas as pd

# Provide file name with path for example: "C:\Users\xxxxx\flights.csv"
split_source_file = input("File Name with absolute Path? : ")

# find number of lines using Pandas
pd_dataframe = pd.read_csv(split_source_file, header=0)
number_of_rows = len(pd_dataframe.index) + 1

# find number of lines using traditional python
# fh = open(split_source_file, 'r')
# for count, line in enumerate(fh):
#     pass
# py_number_of_rows = count

logging.info(f"{number_of_rows} rows")

# Incase of equal split, provide the same number for min and max
min_rows = int(input("Minimum Number of rows per file? : "))
max_rows = int(input("Maximum Number of rows per file? : "))

file_increment = 1
skip_rows = 1

# first file random numbers
number_of_rows_perfile = random.randint(min_rows, max_rows)
header = pd.read_csv(split_source_file, nrows=0).columns.tolist()

while True:
    if number_of_rows_perfile <= 0:
        break

    # Read CSV file with number of rows and skip respective number of lines
    df = pd.read_csv(
        split_source_file, header=0, nrows=number_of_rows_perfile, skiprows=skip_rows
    )
    # Target file name
    split_target_file = f"{split_source_file[:-4]}_{file_increment}.csv"
    # write to csv

    df.to_csv(
        split_target_file,
        index=False,
        header=header,
        mode="a",
        chunksize=number_of_rows_perfile,
    )
    logging.info("Split %d rows into %s" % (number_of_rows_perfile, split_target_file))

    file_increment += 1
    skip_rows += number_of_rows_perfile
    # Last file handler
    if skip_rows >= number_of_rows:
        number_of_rows_perfile = number_of_rows - skip_rows
    else:
        number_of_rows_perfile = random.randint(min_rows, max_rows)
