#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
The script to generate weekly arena information page. It has one argument,
which is the path to the data tables.
date_info/arena_types/arena_enemies will be changed every week, which
need to be filled by hand.
"""

import csv
import os
import sys

f = open(os.path.join("./local_files", "weekly_arena_output.txt"), "w")
arena_enemie_dict = {}
units = {}
resists = {}
skill_effects = {}
skills = {}
chinese_numbers = ["一", "二", "三", "四", "五", "六", "七"]
DATA_DIR = sys.argv[1]
elements = ["日", "月", "火", "水", "木", "金", "土", "星"]

with open(os.path.join(DATA_DIR, "ResistTable.csv")) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        weak = ""
        resist = ""
        for ele in range(8):
            k = int(row["element" + str(ele + 1) + "_resistance"])
            if k == 0:
                weak += elements[ele]
            elif k == 2:
                resist += elements[ele]
        resists[row["id"]] = (weak, resist)

with open(os.path.join(DATA_DIR, "UnitTable.csv")) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        units[row["id"]] = row["name"] + row["symbol_name"]

with open(os.path.join(DATA_DIR, "SkillEffectTable.csv")) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        skill_effects[row["id"]] = row["description"]

with open(os.path.join(DATA_DIR, "SkillTable.csv")) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        effect_strs = []
        for effect in range(3):
            if row["effect" + str(effect + 1) + "_id"] == "0":
                continue
            effect_strs.append(skill_effects[row["effect" + str(effect + 1) + "_id"]])
        skills[row["id"]] = "，".join(effect_strs)

with open(os.path.join(DATA_DIR, "ArenaEnemyTable.csv")) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        if int(row["id"]) >= 200001 and int(row["id"]) < 300000:
            skill_strs = []
            for skill in range(3):
                if row["skill" + str(skill + 1) + "_id"] == "0":
                    continue
                skill_strs.append(skills[row["skill" + str(skill + 1) + "_id"]])
            barrier_str = chinese_numbers[int(row["barrier_count"]) - 1] + "盾"
            weak, resist = resists[row["resist_id"]]
            arena_enemie_dict[int(row["unit_id"])] = (
                units[row["unit_id"]],
                barrier_str,
                weak,
                resist,
                "。".join(skill_strs) + "。",
            )


def replace_color(skill):
    skill = skill.replace("<color", "<font color")
    skill = skill.replace("</color>", "</font>")
    return skill


date_info = "周擂台2024年1月8日至2024年1月14日"
arena_types = [["防御", "攻击"], ["支援", "破坏"], ["技巧", "速攻"], ["回复", "干扰"]]
arena_enemies = [
    [  # arena1
        [1049, 3004, 2024],  # stage1
        [2011, 5052, 1016],  # stage2
        [1024],  # stage3
    ],
    [  # arena2
        [3005, 1062],  # stage1
        [1035, 1022, 1107],  # stage2
        [1077, 1033, 1100],  # stage3
    ],
    [  # arena3
        [2044, 1044, 1059],  # stage1
        [1010],  # stage2
        [3002, 2010],  # stage3
    ],
    [  # arena4
        [1059, 2032],  # stage1
        [1102, 2030],  # stage2
        [5053, 1091, 1012],  # stage3
    ],
]


f.write('<div style="overflow:auto">\n')
f.write(date_info + "\n")
f.write(
    """\
{| class="wikitable" style="text-align:center;width:100%"
|-
|角色
|头像
|盾数
|弱点
|耐性
|技能
"""
)
for index, arena_type in enumerate(arena_types):
    type1, type2 = arena_type
    f.write("|-\n")
    f.write(
        "!colspan=6|<font color=red>"
        + type1
        + "/"
        + type2
        + ("阳" if index % 2 == 0 else "阴")
        + "擂台</font>\n"
    )
    enemies = arena_enemies[index]
    for stage in range(3):
        f.write("|-\n")
        f.write("!colspan=6|第" + chinese_numbers[stage] + "面\n")
        stage_enemies = enemies[stage]
        for enemy_id in stage_enemies:
            f.write("|-\n")
            name, barrier_str, weak, resist, skill = arena_enemie_dict[enemy_id]
            f.write("|" + name + "\n")
            f.write("|[[文件:S" + str(enemy_id) + "01.png|25px|link=]]\n")
            f.write("|" + barrier_str + "\n")
            f.write("|" + '<font color="red">' + weak + "</font>\n")
            f.write("|" + '<font color="blue">' + resist + "</font>\n")
            f.write("|" + replace_color(skill) + "\n")
f.write(
    """|}
</div>"""
)

f.write(
    """

{{文章戳
|文章上级页面=周擂台
|时间=
|作者=
|是否原创=是
|来源=
|原文地址=
}}

[[分类:周擂台]]
"""
)
