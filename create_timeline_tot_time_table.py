import csv
import json
import os
import re
import sys

dir_to_jsons = sys.argv[1]
absent_file = os.path.join("./local_files", "timeline_duration_absent.csv")
#assert os.path.exists(absent_file)

# We will create two csv files.
# One without id and absent_units, and is kept tracking in git
# The other with id and absent_units, which is used for remote data base
output_noid_path = os.path.join("./tracking_files", "TimelineDurationTable_without_id.csv")
output_path = os.path.join("./local_files", "TimelineDurationTable.csv")

all_hit_check_info = []

for json_file_name in sorted(os.listdir(dir_to_jsons)):
    g = re.findall("^TB([0-9]+)([12347])([0123]).json", json_file_name)
    assert len(g) > 0
    g = g[0]
    unit_id = int(g[0])
    barrage_id = int(g[1])
    boost_id = int(g[2])
    if boost_id != 0:
        continue
    json_data = json.load(open(os.path.join(dir_to_jsons, json_file_name)))
    hit_check_order = ""
    stopcast_time = None
    if barrage_id < 3:
        stopcast_time = 0
    fade_time = None
    for order in json_data["order_list"]:
        assert len(order.keys()) == 1
        order_name = list(order.keys())[0]
        if barrage_id < 3:
            if order_name == "EndOrder":
                order_detail = order[order_name]
                fade_time = order_detail["m_boot"]
        else:
            if order_name == "StopCastOrder":
                order_detail = order[order_name]
                stopcast_time = order_detail["m_boot"]
            if order_name == "FadeOrder":
                order_detail = order[order_name]
                fade_time = order_detail["m_boot"]
    if stopcast_time is None or fade_time is None:
        continue
    time1 = fade_time
    time2 = fade_time - stopcast_time
    time3 = time2 / 2
    all_hit_check_info.append((unit_id, barrage_id, time1, time2, time3))

with open(output_noid_path, "w") as fo_noid:
    fo_noid.write("unit_id,barrage_id,time1,time2,time3\n")
    for hit_check_info in sorted(all_hit_check_info):
        unit_id, barrage_id, time1, time2, time3 = hit_check_info
        fo_noid.write(
            str(unit_id)
            + ","
            + str(barrage_id)
            + ","
            + ("%.2f" % time1)
            + ","
            + ("%.2f" % time2)
            + ","
            + ("%.2f" % time3)
            + "\n"
        )

    # add absent unit hit check order info
    #with open(absent_file) as csvfile:
    #    reader = csv.DictReader(csvfile)
    #    for row in reader:
    #        all_hit_check_info.append(
    #            (
    #                int(row["unit_id"]),
    #                int(row["barrage_id"]),
    #                int(row["boost_id"]),
    #                row["hit_check_order"],
    #            )
    #        )

with open(output_path, "w") as fo:
    fo.write("id,unit_id,barrage_id,time1,time2,time3\n")
    uniq_id = 1
    for hit_check_info in sorted(all_hit_check_info):
        unit_id, barrage_id, time1, time2, time3 = hit_check_info
        fo.write(
            str(uniq_id)
            + ","
            + str(unit_id)
            + ","
            + str(barrage_id)
            + ","
            + ("%.2f" % time1)
            + ","
            + ("%.2f" % time2)
            + ","
            + ("%.2f" % time3)
            + "\n"
        )
        uniq_id += 1
