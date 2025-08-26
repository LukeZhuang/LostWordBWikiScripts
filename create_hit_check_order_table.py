import csv
import json
import os
import re
import sys

dir_to_jsons = sys.argv[1]
absent_file = os.path.join("./local_files", "hit_check_order_absent.csv")
assert os.path.exists(absent_file)

# We will create two csv files.
# One without id and absent_units, and is kept tracking in git
# The other with id and absent_units, which is used for remote data base
output_noid_path = os.path.join("./tracking_files", "HitCheckOrderTable_without_id.csv")
output_path = os.path.join("./local_files", "HitCheckOrderTable.csv")

all_hit_check_info = []

for json_file_name in sorted(os.listdir(dir_to_jsons)):
    g = re.findall("^TB([0-9]+)([12347])([0123]).json", json_file_name)
    assert len(g) > 0
    g = g[0]
    unit_id = int(g[0])
    barrage_id = int(g[1])
    boost_id = int(g[2])
    json_data = json.load(open(os.path.join(dir_to_jsons, json_file_name)))
    hit_check_order = ""
    for order in json_data["order_list"]:
        assert len(order.keys()) == 1
        order_name = list(order.keys())[0]
        if order_name == "HitCheckOrder" or order_name == "HitCheckAllOrder":
            order_detail = order[order_name]
            hit_check_order += str(order_detail["m_mgznid"] + 1)
    all_hit_check_info.append((unit_id, barrage_id, boost_id, hit_check_order))

# add absent unit hit check order info
with open(absent_file) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        all_hit_check_info.append(
            (
                int(row["unit_id"]),
                int(row["barrage_id"]),
                int(row["boost_id"]),
                row["hit_check_order"],
            )
        )

with open(output_noid_path, "w") as fo_noid:
    fo_noid.write("unit_id,barrage_id,boost_id,hit_check_order\n")
    for hit_check_info in sorted(all_hit_check_info):
        unit_id, barrage_id, boost_id, hit_check_order = hit_check_info
        fo_noid.write(
            str(unit_id)
            + ","
            + str(barrage_id)
            + ","
            + str(boost_id)
            + ","
            + (hit_check_order if len(hit_check_order) > 0 else "(empty)")
            + "\n"
        )

with open(output_path, "w") as fo:
    fo.write("id,unit_id,barrage_id,boost_id,hit_check_order\n")
    uniq_id = 1
    for hit_check_info in sorted(all_hit_check_info):
        unit_id, barrage_id, boost_id, hit_check_order = hit_check_info
        fo.write(
            str(uniq_id)
            + ","
            + str(unit_id)
            + ","
            + str(barrage_id)
            + ","
            + str(boost_id)
            + ","
            + (hit_check_order if len(hit_check_order) > 0 else "(empty)")
            + "\n"
        )
        uniq_id += 1
