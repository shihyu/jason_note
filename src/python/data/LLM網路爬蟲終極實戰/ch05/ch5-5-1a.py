import csv

csvfile = "Example2.csv"
list1 = [[10,33,45], [5, 25, 56]]
with open(csvfile, 'w+', newline='') as fp:
    writer = csv.writer(fp)
    writer.writerow(["Data1","Data2","Data3"])
    for row in list1:
        writer.writerow(row)
        