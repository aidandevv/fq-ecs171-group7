from cleantext import clean
from unidecode import unidecode
import string
import csv
import re

punct_to_remove = string.punctuation.replace(",", "")

punct_pattern = "[" + re.escape(punct_to_remove) + "]"

with open('mergedTwo.csv', 'r', encoding='utf-8') as infile, \
     open('mergedClean.csv', 'w', encoding='utf-8', newline='') as outfile:
    
    reader = csv.reader(infile)
    writer = csv.writer(outfile)

    for row in reader:
        lyrics = row[2]

        cleaned = clean(
            lyrics,
            fix_unicode=True,
            to_ascii=True,          
            lower=False,
            no_currency_symbols=True,
            no_line_breaks=True
        )

        cleaned = unidecode(cleaned)

        cleaned = re.sub(punct_pattern, "", cleaned)

        row[2] = cleaned
        writer.writerow(row)