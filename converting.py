import csv
import json

# Read CSV and convert to JSON
csv_file = 'eateries.csv'
json_file = 'eateries.json'

data = []
with open(csv_file, encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        data.append(row)

with open(json_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4)
