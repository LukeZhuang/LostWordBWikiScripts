import sys
import csv

original_table = sys.argv[1]
unit_table = sys.argv[2]

units = {}

with open(unit_table) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        units[row["id"]] = row["name"] + row["symbol_name"]

barrage_map = {"1": "扩散", "2": "集中", "3": "一符", "4": "二符", "7": "终符"}

fo = open("./local_files/TimelineDurationTable_readable.csv", "w")
fo.write("unit_id,barrage_id,不按加速,按加速\n")
with open(original_table) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        unit_id = row["unit_id"]
        unit_name = units[unit_id] if unit_id in units else unit_id
        fo.write(
            unit_name
            + ","
            + barrage_map[row["barrage_id"]]
            + ","
            + row["time1"]
            + ","
            + row["time3"]
            + "\n"
        )
fo.close()
