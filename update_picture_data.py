#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Generate a JSON file containing the information of the new pictures
for incrementally updating on the TouhouLostword BWiki site.
There are two arguments, which is the old PictureTable.csv and the new one.
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

workspace_dir = os.path.join(".", "local_files")
picture_table_file_old = sys.argv[1]
picture_table_file_new = sys.argv[2]
range_dict = {"0": "自身", "1": "自身", "2": "己方全体", "3": "敌方单体", "4": "敌方全体"}
role_dict = {
    "21": "防御式",
    "31": "防御式",
    "22": "支援式",
    "32": "支援式",
    "23": "回复式",
    "33": "回复式",
    "24": "干扰式",
    "34": "干扰式",
    "25": "攻击式",
    "35": "攻击式",
    "26": "技巧式",
    "36": "技巧式",
    "27": "速攻式",
    "37": "速攻式",
    "28": "破坏式",
    "38": "破坏式",
}
buff_dict = {
    "1": "阳攻",
    "2": "阳防",
    "3": "阴攻",
    "4": "阴防",
    "5": "速度",
    "6": "命中",
    "7": "回避",
    "8": "会心攻击",
    "9": "会心防御",
    "10": "会心命中",
    "11": "会心回避",
    "12": "仇恨值",
}
bullet_dict = {
    "1": "通常弹",
    "2": "镭射弹",
    "3": "体术弹",
    "4": "斩击弹",
    "5": "动能弹",
    "6": "流体弹",
    "7": "能量弹",
    "8": "御符弹",
    "9": "光弹",
    "10": "尖头弹",
    "11": "追踪弹",
}
element_dict = {
    "1": "日",
    "2": "月",
    "3": "火",
    "4": "水",
    "5": "木",
    "6": "金",
    "7": "土",
    "8": "星",
    "9": "无",
}
other_dict = {"3": "体力回复", "4": "结界回复", "5": "灵力上升", "17": "灵力回收效率"}
picture_type_dict = {"1": "梅", "2": "兰", "3": "菊", "4": "竹"}
correction_type_dict = {
    "1": "体力",
    "2": "阳攻",
    "3": "阳防",
    "4": "阴攻",
    "5": "阴防",
    "6": "速度",
}


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


def adjust_text_for_html(text: str) -> str:
    return (
        text.replace("<color=", "<font color=")
        .replace("</color>", "</font>")
        .replace("<ret>", "<br>")
    )


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

pictures_json: dict[str, dict[str, str]] = {}
for row in reader:
    name = row["name"]

    buffs_str = ""
    debuffs_str = ""
    ranges_str = ""
    bullet_types_str = ""
    element_types_str = ""
    other_effects_str = ""
    role_types_str = ""

    effects = [
        row["picture_characteristic" + str(i + 1) + "_effect_type"] for i in range(3)
    ]
    subtypes = [
        row["picture_characteristic" + str(i + 1) + "_effect_subtype"] for i in range(3)
    ]
    ranges = [
        row["picture_characteristic" + str(i + 1) + "_effect_range"] for i in range(3)
    ]

    for j in range(3):
        if int(effects[j]) in [1] + list(range(21, 29)):
            buffs_str += buff_dict[subtypes[j]] + "、"
        if int(effects[j]) in [2] + list(range(31, 39)):
            debuffs_str += buff_dict[subtypes[j]] + "、"
        if int(effects[j]) in [3, 4, 5, 17]:
            other_effects_str += other_dict[effects[j]] + "、"
        if int(effects[j]) in [15]:
            bullet_types_str += bullet_dict[subtypes[j]] + "、"
        if int(effects[j]) in [16]:
            element_types_str += element_dict[subtypes[j]] + "、"
        if int(effects[j]) in list(range(21, 29)) + list(range(31, 39)):
            role_types_str += role_dict[effects[j]] + "、"
        ranges_str += range_dict[ranges[j]] + "、"

    correction1_type_str = correction_type_dict[row["correction1_type"]]
    correction2_type_str = correction_type_dict[row["correction2_type"]]
    correction1_value = int(row["correction1_value"])
    correction2_value = int(row["correction2_value"])
    correction1_diff = int(row["correction1_diff"])
    correction2_diff = int(row["correction2_diff"])
    correction1_value0 = correction1_value - 10 * correction1_diff
    correction2_value0 = correction2_value - 10 * correction2_diff
    six_value = {
        correction1_type_str: correction1_value,
        correction2_type_str: correction2_value,
    }

    picture_dict = {
        "名称": name,
        "编号": row["id"],
        "类型": picture_type_dict[row["type"]],
        "稀有度": row["rare"],
        "画师": row["illustrator_name"],
        "buff类型": buffs_str,
        "debuff类型": debuffs_str,
        "作用范围": ranges_str,
        "弹种": bullet_types_str,
        "特性属性": element_types_str,
        "其他效果": other_effects_str,
        "角色式限定": role_types_str,
        "查询属性": correction1_type_str + "、" + correction2_type_str,
        "属性1": correction1_type_str,
        "属性2": correction2_type_str,
        "0级属性1": str(correction1_value0),
        "0级属性2": str(correction2_value0),
        "10级属性1": str(correction1_value),
        "10级属性2": str(correction2_value),
        "体力": str(six_value.get("体力", "")),
        "阳攻": str(six_value.get("阳攻", "")),
        "阳防": str(six_value.get("阳防", "")),
        "阴攻": str(six_value.get("阴攻", "")),
        "阴防": str(six_value.get("阴防", "")),
        "速度": str(six_value.get("速度", "")),
        "属性每级强化": correction1_type_str
        + "+"
        + str(correction1_diff)
        + " "
        + correction2_type_str
        + "+"
        + str(correction2_diff),
        "获取途径": "国服暂无",  # default, need to modify by hand later
        "特性1": adjust_text_for_html(row["picture_characteristic_text"]),
        "特性2": adjust_text_for_html(row["picture_characteristic_text_max"]),
        "特性1简缩": "",
        "特性2简缩": "",
        "解说1": adjust_text_for_html(row["flavor_text1"]),
        "解说2": adjust_text_for_html(row["flavor_text2"]),
        "解说3": adjust_text_for_html(row["flavor_text3"]),
        "解说4": adjust_text_for_html(row["flavor_text4"]),
        "解说5": adjust_text_for_html(row["flavor_text5"]),
    }
    pictures_json[name] = picture_dict

output_file_path = os.path.join(workspace_dir, "pictures_wikidata.json")
with open(output_file_path, "w", encoding="utf-8") as fo:
    json_string = json.dumps(
        pictures_json, ensure_ascii=False, separators=(",\n", ": ")
    )
    fo.write(json_string)
