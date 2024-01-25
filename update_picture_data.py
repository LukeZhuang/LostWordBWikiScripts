#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Generate a JSON file containing the information of the new pictures
for incrementally updating on TouhouLostword BWiki site.
There are two arguments which is the old PictureTable.csv and the new one.
To do batch update on BWIKI, copy/paste the JSON output as well as the
batch_content_for_pictures.txt to the webpage.
This script is modified based on 魔多魔多罗's script.
"""

import csv
import json
import os
import re
import sys
from difflib import Differ

workspace_dir = os.path.join(".", "files")
picture_table_file_old = sys.argv[1]
picture_table_file_new = sys.argv[2]
range_dict = {0: "自身", 1: "自身", 2: "己方全体", 3: "敌方单体", 4: "敌方全体"}
character_dict = {
    21: "防御式",
    31: "防御式",
    22: "支援式",
    32: "支援式",
    23: "回复式",
    33: "回复式",
    24: "干扰式",
    34: "干扰式",
    25: "攻击式",
    35: "攻击式",
    26: "技巧式",
    36: "技巧式",
    27: "速攻式",
    37: "速攻式",
    28: "破坏式",
    38: "破坏式",
}
buff_dict = {
    1: "阳攻",
    2: "阳防",
    3: "阴攻",
    4: "阴防",
    5: "速度",
    6: "命中",
    7: "回避",
    8: "会心攻击",
    9: "会心防御",
    10: "会心命中",
    11: "会心回避",
    12: "仇恨值",
}
bullet_dict = {
    1: "通常弹",
    2: "镭射弹",
    3: "体术弹",
    4: "斩击弹",
    5: "动能弹",
    6: "流体弹",
    7: "能量弹",
    8: "御符弹",
    9: "光弹",
    10: "尖头弹",
    11: "追踪弹",
}
element_dict = {1: "日", 2: "月", 3: "火", 4: "水", 5: "木", 6: "金", 7: "土", 8: "星", 9: "无"}
other_dict = {3: "体力回复", 4: "结界回复", 5: "灵力上升", 17: "灵力回收效率"}
picture_type_dict = {1: "梅", 2: "兰", 3: "菊", 4: "竹"}
correction_type_dict = {1: "体力", 2: "阳攻", 3: "阳防", 4: "阴攻", 5: "阴防", 6: "速度"}


def remove_is_show(file_path: str) -> list[str]:
    output_lines = []
    with open(file_path) as csvfile:
        for line in csvfile:
            fields = line.strip().split()
            if fields[0] == "id":
                assert fields[-1] == "is_show"
            new_line = re.sub(r",(is_show|0|1)$", "", line.strip())
            output_lines.append(new_line)
    return output_lines


old_lines = remove_is_show(picture_table_file_old)
new_lines = remove_is_show(picture_table_file_new)
# check headers are the same
assert old_lines[0] == new_lines[0] and old_lines[0].startswith("id")

# get the new pic content (or the ones that needed to be updated) using difflib
csv_differ = Differ()
pic_diff_csv = [
    diff_line[2:]
    for diff_line in csv_differ.compare(old_lines, new_lines)
    if diff_line.startswith("+ ")
]
pic_diff_csv = [old_lines[0]] + pic_diff_csv

reader = csv.DictReader(pic_diff_csv)

for row in reader:
    print(row)
