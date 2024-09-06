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

fo = open("./local_files/HitCheckOrderTable_readable.csv", "w")
with open(original_table) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        if row["boost_id"] != "3":
            continue
        fo.write(
            units[row["unit_id"]]
            + ","
            + barrage_map[row["barrage_id"]]
            + ","
            + row["hit_check_order"]
            + "\n"
        )
fo.close()
