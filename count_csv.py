import csv
from pathlib import Path

path = Path('sample_transactions.csv')
with path.open(newline='', encoding='utf-8') as f:
    count = sum(1 for _ in csv.reader(f))
print(count)
