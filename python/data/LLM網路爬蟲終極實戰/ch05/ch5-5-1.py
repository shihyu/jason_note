import csv

csvfile = "Example.csv"
with open(csvfile, 'r') as fp:
    reader = csv.reader(fp)
    for row in reader:
        print(','.join(row))
        