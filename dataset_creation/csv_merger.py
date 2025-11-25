import pandas as pd
import sys
import os

csv1_path = sys.argv[1]
csv2_path = sys.argv[2]
output_csv_path = sys.argv[3]

if not os.path.exists(csv1_path):
  raise NameError(csv1_path, "does not exist")

if not os.path.exists(csv2_path):
  raise NameError(csv2_path, "does not exist")

df1 = pd.read_csv(csv1_path)
df2 = pd.read_csv(csv2_path)

columns = ["Artist", "TrackName"]

merged = pd.concat((df1, df2)).sample(frac=1)

duplicated_rows_mask = merged.duplicated(columns, keep=False)
duplicated_rows = merged.loc[duplicated_rows_mask, columns].copy()

if duplicated_rows.empty:
  print("No Duplicated Rows were found, CSV file has been created")
  merged.to_csv(output_csv_path, index=False)
else:
  print("Duplicated rows found, please resolve:")
  print(duplicated_rows)
