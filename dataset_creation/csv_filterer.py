import csv
from better_profanity import profanity

profanity.load_censor_words()

with open('data/kidsTwo.csv', 'r', newline='', encoding='utf-8') as infile, \
     open('data/kidsTwo_cleaned.csv', 'w', newline='', encoding='utf-8') as cleanfile, \
     open('data/kidsTwo_filtered.csv', 'w', newline='', encoding='utf-8') as filteredfile:

    reader = csv.reader(infile)
    clean_writer = csv.writer(cleanfile)
    filtered_writer = csv.writer(filteredfile)

    for row in reader:
        lyrics = row[2]

        if profanity.contains_profanity(lyrics):
            filtered_writer.writerow(row)
        else:
            clean_writer.writerow(row)
