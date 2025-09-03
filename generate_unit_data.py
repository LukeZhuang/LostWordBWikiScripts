#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
"""

import csv
from collections import OrderedDict
import copy
import json
import os
import shutil
import sys
from tqdm import tqdm


dir_to_data = sys.argv[1]

if os.path.exists(os.path.join("./tracking_files", "characters_wikidata.json")):
    shutil.copyfile(
        os.path.join("./tracking_files", "characters_wikidata.json"),
        os.path.join("./local_files", "old_characters_wikidata.json"),
    )

effect_icon_size = 20
Elements = {1: "日", 2: "月", 3: "火", 4: "水", 5: "木", 6: "金", 7: "土", 8: "星", 9: "无"}
BulletCategory = {
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
Roles = {1: "防御式", 2: "支援式", 3: "回复式", 4: "干扰式", 5: "攻击式", 6: "技巧式", 7: "速攻式", 8: "破坏式"}
RareCategory = {
    1: "常驻/限定",
    2: "超限定",
    3: "Relic限定",
    4: "Epic限定",
    5: "Genic限定",
    2.5: "EX限定",
    648: "白FES限定",
    0.5: "油库里",
    2.25: "通行证限定",
}
AbnormalCategory = {1: "燃烧", 2: "冻结", 3: "感电", 4: "毒雾", 5: "黑暗"}
AbnormalCategoryEng = {
    1: "burning",
    2: "frozen",
    3: "electrified",
    4: "poisoning",
    5: "blackout",
}
AbnormalSimpleCategory = {1: "烧", 2: "冰", 3: "电", 4: "毒", 5: "暗"}
BuffEffectCategory = {
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
    12: "仇恨",
    103: "阳攻阴攻",
    106: "阳攻命中",
    108: "阳攻会心攻击",
    110: "阳攻会心命中",
    211: "阳防会心回避",
    308: "阴攻会心攻击",
}
AbnormalBreakCategory = {12: "焚灭", 13: "融冰", 14: "放电", 15: "猛毒", 16: "闪光"}
VoiceCategory = {
    1: "语音 自我介绍",
    2: "语音 紫心",
    3: "语音 蓝心",
    4: "语音 绿心",
    5: "语音 橙心",
    6: "语音 粉心",
    7: "语音 转生",
    8: "语音 强化完成",
    9: "语音 登录",
    10: "语音 主页1",
    11: "语音 主页2",
    12: "语音 主页3",
    13: "语音 春",
    14: "语音 夏",
    15: "语音 秋",
    16: "语音 冬",
    17: "语音 任务",
    18: "语音 任务完成",
    19: "语音 信箱",
    20: "语音 归来",
    21: "语音 派遣完成",
    22: "语音 反应1",
    23: "语音 反应2",
    24: "语音 反应3",
    25: "语音 战斗开始",
    26: "语音 进入下波战斗",
    27: "语音 胜利",
    28: "语音 败北",
    29: "语音 增幅1",
    30: "语音 增幅2",
    31: "语音 增幅3",
    32: "语音 擦弹1",
    33: "语音 擦弹2",
    34: "语音 擦弹3",
    35: "语音 技能A",
    36: "语音 技能B",
    37: "语音 指令A",
    38: "语音 指令B",
    39: "语音 指令C",
    40: "语音 指令D",
    41: "语音 换人退场",
    42: "语音 换人登场",
    43: "语音 射击A",
    44: "语音 射击B",
    45: "语音 符卡A口述1",
    46: "语音 符卡A口述2",
    47: "语音 符卡A宣言",
    48: "语音 符卡B口述1",
    49: "语音 符卡B口述2",
    50: "语音 符卡B宣言",
    51: "语音 终符口述1",
    52: "语音 终符口述2",
    53: "语音 终符宣言",
    54: "语音 伤害",
    55: "语音 大伤害",
    56: "语音 卡片",
    57: "语音 擦弹发动",
    58: "语音 增幅·回复",
    59: "语音 无法战斗",
    60: "语音 标题",
    61: "语音 肯定回答",
    62: "语音 否定回答",
    63: "语音 感谢",
    64: "语音 低声自语",
    65: "语音 决胜台词",
}


def is_fake_unit(unit_data):
    return unit_data["symbol_name"] == "" or unit_data["alias_name"] == "_TEST"


def file_maker(name, size):
    return "[[File:" + name + "|" + str(size) + "px]]".replace("#", "")


def tegong_maker(name):
    return "[" + name + "特攻]"


def bullet_effect_maker(name, rate, description):
    if rate == -1:
        return "[" + name + "]" + description
    return "[" + name + "]" + "[" + str(rate) + "%]" + description


allowed_chars = (
    [chr(i) for i in range(ord("A"), ord("Z") + 1)]
    + [chr(i) for i in range(ord("a"), ord("z") + 1)]
    + [chr(i) for i in range(ord("0"), ord("9") + 1)]
    + [".", "&", "#", ">", "=", "<", "$"]
)


def check_chars(c_mark):
    for c in c_mark:
        assert c in allowed_chars


def replace_mark(s):
    new_s = s
    new_s = new_s.replace("#", "＃")
    new_s = new_s.replace(">", "＞")
    new_s = new_s.replace("&", "＆")
    new_s = new_s.replace("=", "＝")
    new_s = new_s.replace("<", "＜")
    new_s = new_s.replace("$", "＄")
    return new_s


def process_cmark(c_mark, c_id):
    check_chars(c_mark)
    new_c_mark = copy.copy(c_mark)
    new_c_mark = replace_mark(new_c_mark)
    if c_id == 2927:
        new_c_mark += "-幻月"
    if c_id == 2937:
        new_c_mark += "-神绮"
    if c_id == 3905:
        new_c_mark += "-魅魔"
    if c_id == 3926:
        new_c_mark += "-梦月"
    return new_c_mark


def load_csv(path_to_csv):
    data = {}
    with open(path_to_csv) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            rowid = int(row["id"])
            assert rowid not in data
            data[rowid] = row
    return data


def load_master_json(table_name):
    data = {}
    with open(os.path.join(dir_to_data, table_name + "Table.json")) as jsonfile:
        for line in jsonfile:
            row = json.loads(line)
            rowid = int(row["id"])
            assert rowid not in data
            data[rowid] = row
    return data


# load master data
unit_datas = load_master_json("Unit")
race_datas = load_master_json("Race")
unit_race_datas = load_master_json("UnitRace")
skill_datas = load_master_json("Skill")
resist_datas = load_master_json("Resist")
ability_datas = load_master_json("Ability")
characteristic_datas = load_master_json("Characteristic")
skill_effect_datas = load_master_json("SkillEffect")
shot_datas = load_master_json("Shot")
spell_card_datas = load_master_json("Spellcard")
bullet_datas = load_master_json("Bullet")
bullet_addon_datas = load_master_json("BulletAddon")
bullet_extra_effect_datas = load_master_json("BulletExtraEffect")
bullet_critical_race_datas = load_master_json("BulletCriticalRace")
bgm_datas = load_master_json("Bgm")
item_datas = load_master_json("Item")
costume_datas = load_master_json("Costume")
person_relation_datas = load_master_json("PersonRelation")
unit_rank_promote_datas = load_master_json("UnitRankPromote")
picture_datas = load_master_json("Picture")
item_datas = load_master_json("Item")
voice_datas = load_master_json("Voice")
voice_set_datas = load_master_json("VoiceSet")

# load custom data
unit_dates = load_csv("./UnitDate.csv")
hit_check_order_raw = load_csv(os.path.join("./local_files/", "HitCheckOrderTable.csv"))
time_duration_raw = load_csv(
    os.path.join("./local_files/", "TimelineDurationTable.csv")
)

# preprocessing
person_id_to_id = {}
for key in unit_datas:
    unit_data = unit_datas[key]
    if is_fake_unit(unit_data):
        continue
    c_id = int(unit_data["id"])
    p_id = int(unit_data["person_id"])
    assert p_id not in person_id_to_id
    person_id_to_id[p_id] = c_id

unit_races = {}
for key in unit_race_datas:
    unit_race_data = unit_race_datas[key]
    c_id = int(unit_race_data["unit_id"])
    if c_id not in unit_races:
        unit_races[c_id] = []
    unit_races[c_id].append(int(unit_race_data["race_id"]))

bullet_critical_races = {}
for key in bullet_critical_race_datas:
    bullet_critical_race_data = bullet_critical_race_datas[key]
    b_id = int(bullet_critical_race_data["bullet_id"])
    if b_id not in bullet_critical_races:
        bullet_critical_races[b_id] = []
    bullet_critical_races[b_id].append(int(bullet_critical_race_data["race_id"]))

unit_costumes = {}
for key in costume_datas:
    costume_data = costume_datas[key]
    c_id = int(costume_data["unit_id"])
    if c_id not in unit_costumes:
        unit_costumes[c_id] = []
    unit_costumes[c_id].append(int(costume_data["id"]))

person_relations = {}
for key in person_relation_datas:
    person_relation_data = person_relation_datas[key]
    p_id1 = int(person_relation_data["person_id"])
    p_id2 = int(person_relation_data["target_person_id"])
    if p_id1 not in person_id_to_id or p_id2 not in person_id_to_id:
        continue
    c_id1 = person_id_to_id[p_id1]
    c_id2 = person_id_to_id[p_id2]
    if c_id1 not in person_relations:
        person_relations[c_id1] = []
    person_relations[c_id1].append(c_id2)

rank_promotes = {}
for key in unit_rank_promote_datas:
    unit_rank_promote_data = unit_rank_promote_datas[key]
    c_id = int(unit_rank_promote_data["unit_id"])
    rank = int(unit_rank_promote_data["rank"])
    if c_id not in rank_promotes:
        rank_promotes[c_id] = {}
    rank_promotes[c_id][rank] = unit_rank_promote_data

voices = {}
for key in voice_datas:
    voice_data = voice_datas[key]
    c_id = int(voice_data["unit_id"])
    v_type = int(voice_data["voice_type_id"])
    v_text = voice_data["voice_text"]
    if c_id not in voices:
        voices[c_id] = {}
    voices[c_id][v_type] = v_text

voice_sets = {}
for key in voice_set_datas:
    voice_set_data = voice_set_datas[key]
    c_id = int(voice_set_data["unit_id"])
    f_id = int(voice_set_data["file_id"])
    if c_id not in voice_sets:
        voice_sets[c_id] = {}
    voice_sets[c_id][f_id] = (voice_set_data["name"], voice_set_data["cast_name"])

time_durations = {}
for key in time_duration_raw:
    time_duration_data = time_duration_raw[key]
    c_id = int(time_duration_data["unit_id"])
    if c_id not in time_durations:
        time_durations[c_id] = {}
    time_durations[c_id][int(time_duration_data["barrage_id"])] = (
        time_duration_data["time1"],
        time_duration_data["time3"],
    )

hit_check_orders = {}
for key in hit_check_order_raw:
    hit_check_order_data = hit_check_order_raw[key]
    boost_id = int(hit_check_order_data["boost_id"])
    if boost_id != 3:
        continue
    c_id = int(hit_check_order_data["unit_id"])
    if c_id not in hit_check_orders:
        hit_check_orders[c_id] = {}
    hit_check_orders[c_id][
        int(hit_check_order_data["barrage_id"])
    ] = hit_check_order_data["hit_check_order"]


def simplify_skill_effect(
    c_id, skill_index, effect_index, generated_description, skill_effect_id
):
    skill_effect_data = skill_effect_datas[skill_effect_id]
    se_type = int(skill_effect_data["type"])
    se_subtype = int(skill_effect_data["subtype"])
    se_range = int(skill_effect_data["range"])

    def skill_effect_raise_exception():
        ud = unit_datas[c_id]
        ud_name = ud["name"] + ud["symbol_name"]
        print(
            c_id,
            ud_name,
            skill_index,
            effect_index,
            generated_description,
            se_type,
            se_subtype,
            se_range,
            "not handled",
        )
        assert False

    result = ""
    if se_type == 1:  # buff
        special = False
        if se_range == 1:
            result += "自身"
        elif se_range == 2:
            result += "我方"
        elif se_range == 3:
            result += "目标"
            special = True
        elif se_range == 4:
            result += "敌方"
            special = True
        else:
            skill_effect_raise_exception()
        if se_subtype == 12:  # 仇恨是特别的，上升下降都正常
            special = False
        if se_subtype not in BuffEffectCategory:
            skill_effect_raise_exception()
        result += BuffEffectCategory[se_subtype]
        if special:
            result += "上升"
    elif se_type == 2:  # debuff
        special = False
        if se_range == 1:
            result += "自身"
            special = True
        elif se_range == 2:
            result += "我方"
            special = True
        elif se_range == 3:
            result += "目标"
        elif se_range == 4:
            result += "敌方"
        else:
            skill_effect_raise_exception()
        if se_subtype == 12:  # 仇恨是特别的，上升下降都正常
            special = False
        if se_subtype not in BuffEffectCategory:
            skill_effect_raise_exception()
        result += BuffEffectCategory[se_subtype]
        if special:
            result += "下降"
    elif se_type == 3:  # 回血
        if se_range == 1:
            result += "自身"
        elif se_range == 2:
            result += "我方"
        else:
            skill_effect_raise_exception()
        result += "回血"
    elif se_type == 4:  # 回盾
        if se_range == 1:
            result += "自身"
        elif se_range == 2:
            result += "我方"
        else:
            skill_effect_raise_exception()
        result += "回盾"
    elif se_type == 5:  # 回灵
        if se_range == 1:
            result += "自身"
        elif se_range == 2:
            result += "我方"
        else:
            skill_effect_raise_exception()
        result += "回灵"
    elif se_type == 6:  # 上异常
        if se_range == 1:
            result += "自身"
        elif se_range == 2:
            result += "我方"
        elif se_range == 3:
            result += "目标"
        elif se_range == 4:
            result += "敌方"
        else:
            skill_effect_raise_exception()
        result += "上" + AbnormalSimpleCategory[se_subtype]
    elif se_type == 8:  # 行动顺序
        if se_range == 1:
            result += "自身"
        elif se_range == 2:
            result += "我方"
        else:
            skill_effect_raise_exception()
        if se_subtype == 1:
            result += "先行"
        elif se_subtype == 2:
            result += "后行"
        else:
            skill_effect_raise_exception()
    elif se_type == 9:  # 恢复结界异常
        if se_range == 1:
            result += "自身"
        elif se_range == 2:
            result += "我方"
        else:
            skill_effect_raise_exception()
        result += "回结界异常"
    elif se_type == 10:  # 开锁
        if se_range == 1:
            result += "自身"
        elif se_range == 2:
            result += "我方"
        else:
            skill_effect_raise_exception()
        result += "开锁"
    elif se_type == 12:  # 受到弹种伤害降低
        if se_range == 1:
            result += "自身"
        elif se_range == 2:
            result += "我方"
        else:
            skill_effect_raise_exception()
        result += BulletCategory[se_subtype]
        result += "防"
    elif se_type == 13:  # 受到属性伤害降低
        if se_range == 1:
            result += "自身"
        elif se_range == 2:
            result += "我方"
        else:
            skill_effect_raise_exception()
        result += Elements[se_subtype]
        result += "防"
    elif se_type == 14:  # 受到某种族伤害降低
        if se_range == 1:
            result += "自身"
        elif se_range == 2:
            result += "我方"
        else:
            skill_effect_raise_exception()
        result += "特防"
    elif se_type == 15:  # 弹种威力上升
        if se_range == 1:
            result += "自身"
        elif se_range == 2:
            result += "我方"
        else:
            skill_effect_raise_exception()
        result += BulletCategory[se_subtype]
        result += "加伤"
    elif se_type == 16:  # 属性威力上升
        if se_range == 1:
            result += "自身"
        elif se_range == 2:
            result += "我方"
        else:
            skill_effect_raise_exception()
        result += Elements[se_subtype]
        result += "加伤"
    elif se_type == 41:  # 二阶buff
        if se_range == 1:
            result += "自身"
        elif se_range == 2:
            result += "我方"
        else:
            skill_effect_raise_exception()
        result += BuffEffectCategory[se_subtype]
    elif se_type == 42:  # 二阶debuff
        if se_range == 3:
            result += "目标"
        elif se_range == 4:
            result += "敌方"
        else:
            skill_effect_raise_exception()
        result += BuffEffectCategory[se_subtype]
    elif se_type == 43:  # 上弱点
        if se_range == 3:
            result += "目标"
        elif se_range == 4:
            result += "敌方"
        else:
            skill_effect_raise_exception()
        result = ""
        result += "加弱"
        result += Elements[se_subtype]
    elif se_type == 46:  # 每回合持续增益
        if se_range == 1:
            result += "自身"
        elif se_range == 2:
            result += "我方"
        else:
            skill_effect_raise_exception()
        result = ""
        result += "缓慢"
        if se_subtype == 3:
            result += "回血"
        elif se_subtype == 4:
            result += "回盾"
        elif se_subtype == 5:
            result += "回灵"
        elif se_subtype == 10:
            result += "开锁"
        else:
            skill_effect_raise_exception()
    elif se_type == 47:  # 共鸣（根据前台角色数量增益）
        if se_range == 1:
            result += "自身"
        elif se_range == 2:
            result += "我方"
        else:
            skill_effect_raise_exception()
        result = ""
        if se_subtype == 5:
            result += "速度"
        elif se_subtype == 6:
            result += "灵力"
        elif se_subtype == 7:
            result += "伤害"
        elif se_subtype == 8:
            result += "暴伤"
        elif se_subtype == 9:
            result += "暴击率"
        else:
            skill_effect_raise_exception()
        result += "共鸣"
    elif se_type == 48:  # 蓄力（根据某些状态加伤）
        if se_range == 1:
            result += "自身"
        elif se_range == 2:
            result += "我方"
        else:
            skill_effect_raise_exception()
        result = ""
        if se_subtype == 3:
            result += "体蓄力"
        elif se_subtype == 4:
            result += "盾蓄力"
        elif se_subtype == 5:
            result += "灵蓄力"
        else:
            skill_effect_raise_exception()
    elif se_type == 49:  # 有利/不利增伤
        if se_range == 1:
            result += "自身"
        elif se_range == 2:
            result += "我方"
        else:
            skill_effect_raise_exception()
        result = ""
        if se_subtype == 1:
            result += "有利增伤"
        elif se_subtype == 2:
            result += "不利增伤"
        else:
            skill_effect_raise_exception()
    elif se_type == 51:  # 减冷却
        if se_range == 1:
            result += "自身"
        elif se_range == 2:
            result += "我方"
        else:
            skill_effect_raise_exception()
        result = ""
        result += "减冷却"
        if se_subtype == 1:
            pass
        else:
            skill_effect_raise_exception()
    elif se_type == 52:  # 符卡延迟
        if se_range == 3:
            result += "目标"
        elif se_range == 4:
            result += "敌方"
        else:
            skill_effect_raise_exception()
        result = ""
        if se_subtype == 2:
            result += "符卡延迟"
        else:
            skill_effect_raise_exception()
    elif se_type == 54:  # 大结界
        result += "大结界"
    elif se_type == 55:  # 油库里共鸣
        if se_range == 1:
            result += "自身"
        elif se_range == 2:
            result += "我方"
        else:
            skill_effect_raise_exception()
        result = ""
        result += "油库里"
        if se_subtype == 5:
            result += "速度共鸣"
        elif se_subtype == 6:
            result += "灵力"
        elif se_subtype == 7:
            result += "伤害"
        elif se_subtype == 8:
            result += "暴伤"
        elif se_subtype == 9:
            result += "暴击率"
        else:
            skill_effect_raise_exception()
        result += "共鸣"
    elif se_type == 57:  # 永久debuff
        if se_range == 3:
            result += "目标"
        elif se_range == 4:
            result += "敌方"
        else:
            skill_effect_raise_exception()
        result += "永久"
        result += BuffEffectCategory[se_subtype]
    elif se_type == 58:  # 属性转换（根据自身某属性加全体某属性）
        if se_range == 1:
            result += "自身"
        elif se_range == 2:
            result += "我方"
        else:
            skill_effect_raise_exception()
        result = ""
        if se_subtype == 5:
            result += "自身速力转我方阳攻"
        elif se_subtype == 14:
            result += "自身阴防转我方阴攻"
        else:
            skill_effect_raise_exception()
    else:
        skill_effect_raise_exception()
    return result


def get_rare_for_wiki(unit_data):
    c_id = int(unit_data["id"])
    c_rare = int(unit_data["limitbreak_item_id"]) - 500

    if int(c_id) == 2937 or int(c_id) == 3905 or int(c_id) == 2927 or int(c_id) == 3926:
        # 秘封组 -> Genic限定（等级为5）
        return 5
    elif int(c_id) == 7037 or int(c_id) == 7038 or int(c_id) == 7039:
        # 白限
        return 648
    elif int(c_id) == 11009:
        # 通行证限定
        return 2.25
    elif int(c_id) >= 50000 and int(c_id) < 60000:
        # 油库里
        return 0.5
    elif c_rare == 3 or c_rare == 4:
        # Epic放Relic前面
        return 7 - c_rare
    elif c_rare == 5:
        # 大限
        return 2.5
    return c_rare


def generate_costume_info(characters, c_id):
    characters["初始皮肤名称"] = ""
    characters["初始皮肤描述"] = ""
    characters["皮肤编号组"] = ""
    characters["皮肤名称组"] = ""
    characters["皮肤描述组"] = ""
    if c_id not in unit_costumes:
        return
    for costume_id in unit_costumes[c_id]:
        costume_data = costume_datas[costume_id]
        if int(costume_data["file_id"]) == 1:
            characters["初始皮肤名称"] = costume_data["name"]
            characters["初始皮肤描述"] = costume_data["description"]
        else:
            if characters["皮肤编号组"] != "":
                characters["皮肤编号组"] += "、"
            if characters["皮肤名称组"] != "":
                characters["皮肤名称组"] += "/"
            if characters["皮肤描述组"] != "":
                characters["皮肤描述组"] += "/"
            characters["皮肤编号组"] += str(costume_data["file_id"]).zfill(2)
            characters["皮肤名称组"] += costume_data["name"]
            characters["皮肤描述组"] += costume_data["description"]


def generate_time_duration(characters, c_id):
    characters["扩散总时长（未加速）"] = ""
    characters["扩散总时长（加速）"] = ""
    characters["集中总时长（未加速）"] = ""
    characters["集中总时长（加速）"] = ""
    characters["1符总时长（未加速）"] = ""
    characters["1符总时长（加速）"] = ""
    characters["2符总时长（未加速）"] = ""
    characters["2符总时长（加速）"] = ""
    characters["终符总时长（未加速）"] = ""
    characters["终符总时长（加速）"] = ""
    if c_id not in time_durations:
        return
    dur = time_durations[c_id]
    characters["扩散总时长（未加速）"] = dur[1][0]
    characters["扩散总时长（加速）"] = dur[1][1]
    characters["集中总时长（未加速）"] = dur[2][0]
    characters["集中总时长（加速）"] = dur[2][1]
    characters["1符总时长（未加速）"] = dur[3][0]
    characters["1符总时长（加速）"] = dur[3][1]
    characters["2符总时长（未加速）"] = dur[4][0]
    characters["2符总时长（加速）"] = dur[4][1]
    characters["终符总时长（未加速）"] = dur[7][0]
    characters["终符总时长（加速）"] = dur[7][1]


def generate_hit_check_order(characters, c_id):
    prefixes = ["扩散", "集中", "1符", "2符", "终符"]
    barrage_ids = [1, 2, 3, 4, 7]
    for prefix in prefixes:
        for i in range(6):
            spell_order_str = prefix + "段落" + str(i + 1)
            characters[spell_order_str] = ""
            characters[spell_order_str + "首发"] = ""
    if c_id not in hit_check_orders:
        return
    for index, prefix in enumerate(prefixes):
        barrage_id = barrage_ids[index]
        hco = hit_check_orders[c_id][barrage_id]
        if "empty" in hco:
            for i in range(6):
                spell_order_str = prefix + "段落" + str(i + 1)
                characters[spell_order_str] = ""
                characters[spell_order_str + "首发"] = ""
        else:
            spell_order = []
            spell_order_count = []
            for i, bullet in enumerate(hco):
                if bullet not in spell_order:
                    spell_order.append(bullet)
                    spell_order_count.append(i + 1)
            for i in range(6):
                spell_order_str = prefix + "段落" + str(i + 1)
                characters[spell_order_str] = int(spell_order[i])
                characters[spell_order_str + "首发"] = spell_order_count[i]


def generate_overall_elements(characters, c_id):
    element_list = []
    for temp_count in range(1, 7):
        if (
            "1符" + str(temp_count) + "属性" in characters
            and characters["1符" + str(temp_count) + "属性"] not in element_list
        ):
            if characters["1符" + str(temp_count) + "属性"] != "无":
                element_list.append(characters["1符" + str(temp_count) + "属性"])
        if (
            "2符" + str(temp_count) + "属性" in characters
            and characters["2符" + str(temp_count) + "属性"] not in element_list
        ):
            if characters["2符" + str(temp_count) + "属性"] != "无":
                element_list.append(characters["2符" + str(temp_count) + "属性"])
        if (
            "终符" + str(temp_count) + "属性" in characters
            and characters["终符" + str(temp_count) + "属性"] not in element_list
        ):
            if characters["终符" + str(temp_count) + "属性"] != "无":
                element_list.append(characters["终符" + str(temp_count) + "属性"])
    temp_string = ""
    for element in element_list:
        temp_string = temp_string + "、" + element
    temp_string = temp_string[1:]
    characters["检索用弹幕属性"] = temp_string


def generate_friendship_characters(characters, c_id):
    characters["羁绊角色"] = ""
    characters["羁绊角色编号"] = ""
    if c_id not in person_relations:
        return
    person_relation = person_relations[c_id]
    characters["羁绊角色"] = "、".join(
        [
            unit_datas[c_id2]["name"] + unit_datas[c_id2]["symbol_name"]
            for c_id2 in person_relation
        ]
    )
    characters["羁绊角色编号"] = "、".join([str(c_id2) for c_id2 in person_relation])


def generate_rank_promote(characters, c_id):
    name_list = ["体力", "阳攻", "阳防", "阴攻", "阴防", "速度"]
    for rank in range(5):
        for slot in range(6):
            item_name_str = "升格" + str(rank + 1) + name_list[slot] + "所需材料"
            item_num_str = item_name_str + "数量"
            characters[item_num_str] = ""
            characters[item_name_str] = ""
    if c_id not in rank_promotes:
        return
    for rank in range(5):
        unit_rank_promote_data = rank_promotes[c_id][rank]
        for slot in range(6):
            item_name_str = "升格" + str(rank + 1) + name_list[slot] + "所需材料"
            item_num_str = item_name_str + "数量"
            item_type = int(
                unit_rank_promote_data["slot" + str(slot + 1) + "_object_type"]
            )
            item_id = int(unit_rank_promote_data["slot" + str(slot + 1) + "_object_id"])
            item_num = int(
                unit_rank_promote_data["slot" + str(slot + 1) + "_object_value"]
            )
            characters[item_num_str] = item_num
            if item_type == 10:
                item_name = (
                    "绘卷图标 "
                    + str(picture_datas[item_id]["id"])
                    + replace_mark(picture_datas[item_id]["name"])
                )
            else:
                assert item_type == 12
                item_name = (
                    item_datas[item_id]["name"].replace("[", "-").replace("]", "-")
                )
            characters[item_name_str] = item_name


def generate_voice(characters, c_id):
    #display_voice_types = [i for i in range(1, 66)]
    display_voice_types = (
        [i for i in range(1, 29)]
        + [i for i in range(41, 45)]
        + [i for i in range(56, 60)]
    )
    for v_type in display_voice_types:
        characters[VoiceCategory[v_type]] = ""
    if c_id not in voices:
        return
    for v_type in display_voice_types:
        characters[VoiceCategory[v_type]] = voices[c_id][v_type]


def generate_cv_info(characters, c_id):
    for cv_id in range(1, 4):
        characters["角色声音" + str(cv_id)] = ""
        characters["角色CV" + str(cv_id)] = ""
    if c_id not in voice_sets:
        return
    for cv_id in range(1, 4):
        if cv_id not in voice_sets[c_id]:
            continue
        sound, cv_name = voice_sets[c_id][cv_id]
        characters["角色声音" + str(cv_id)] = sound
        characters["角色CV" + str(cv_id)] = cv_name


def fixup_return_line(characters):
    for key in characters:
        if isinstance(characters[key], str):
            characters[key] = characters[key].replace("\n", "<br>")


characters_json = {}
for key in tqdm(unit_datas):
    unit_data = unit_datas[key]

    if is_fake_unit(unit_data):
        continue

    # 基础属性
    c_id = int(unit_data["id"])
    c_name = unit_data["name"]
    c_title = unit_data["alias_name"]
    c_name_short = unit_data["short_name"]
    c_mark = unit_data["symbol_name"]
    c_symbol_title = unit_data["symbol_title"]
    c_symbol_description = unit_data["symbol_description"]
    page_name = c_name + process_cmark(c_mark, c_id)
    c_drop_text = unit_data["drop_text"]
    c_role = Roles[int(unit_data["role"])]
    c_rare = get_rare_for_wiki(unit_data)
    c_bgm_id = int(unit_data["spellcard_bgm_id"])
    c_bgm = bgm_datas[c_bgm_id]["name"] if c_bgm_id != 0 else "没有BGM"
    c_race_ids = unit_races.get(c_id, [])
    c_race = "、".join([race_datas[race_id]["name"] for race_id in c_race_ids])
    c_date = unit_dates[c_id]["date"] if c_id in unit_dates else "暂未实装"

    # 满级面板
    c_lp = int(unit_data["life_point"])
    c_yang_atk = int(unit_data["yang_attack"])
    c_yang_def = int(unit_data["yang_defense"])
    c_yin_atk = int(unit_data["yin_attack"])
    c_yin_def = int(unit_data["yin_defense"])
    c_speed = int(unit_data["speed"])

    # 气质
    c_resist_id = int(unit_data["resist_id"])
    c_resist_name = resist_datas[c_resist_id]["name"]
    c_resist_description = resist_datas[c_resist_id]["description"]
    c_resist_ri = int(resist_datas[c_resist_id]["element1_resistance"])
    c_resist_yue = int(resist_datas[c_resist_id]["element2_resistance"])
    c_resist_huo = int(resist_datas[c_resist_id]["element3_resistance"])
    c_resist_shui = int(resist_datas[c_resist_id]["element4_resistance"])
    c_resist_mu = int(resist_datas[c_resist_id]["element5_resistance"])
    c_resist_jin = int(resist_datas[c_resist_id]["element6_resistance"])
    c_resist_tu = int(resist_datas[c_resist_id]["element7_resistance"])
    c_resist_xing = int(resist_datas[c_resist_id]["element8_resistance"])

    # 能力描述
    ability_data = ability_datas[int(unit_data["ability_id"])]
    c_ability_name = ability_data["name"]
    c_ability_description = ability_data["description"]
    c_ability_effect_resist = ability_data["resist_ability_description"]
    c_ability_effect_element = ability_data["element_ability_description"]
    c_ability_effect_barrier = ability_data["barrier_ability_description"]
    c_ability_effect_boost = ability_data["boost_ability_description"]
    c_ability_effect_purge = ability_data["purge_ability_description"]
    c_ability_effect_summary = []
    if c_ability_effect_resist != "":
        c_ability_effect_summary.append(c_ability_effect_resist)
    if c_ability_effect_element != "":
        c_ability_effect_summary.append(c_ability_effect_element)
    if c_ability_effect_barrier != "":
        c_ability_effect_summary.append(c_ability_effect_barrier)
    if c_ability_effect_boost != "":
        c_ability_effect_summary.append(c_ability_effect_boost)
    if c_ability_effect_purge != "":
        c_ability_effect_summary.append(c_ability_effect_purge)
    c_ability_effect_summary = "<br>".join(c_ability_effect_summary)
    c_ability_effect_summary = c_ability_effect_summary.replace(
        "<color=", "<font color="
    ).replace("</color>", "</font>")

    # 结界异常效果（燃烧，冻结，感电，毒雾，黑暗）
    c_ability_abnormal = [0] + [
        int(ability_data[AbnormalCategoryEng[i] + "_barrier_type"]) for i in range(1, 6)
    ]

    def get_abnormal_set(effect_id):
        abnormal_ids = [i for i, v in enumerate(c_ability_abnormal) if v == effect_id]
        return "、".join([AbnormalCategory[x] for x in abnormal_ids])

    # 强化能力效果
    c_ability_boost_type = int(ability_data["boost_power_divergence_type"])
    c_ability_boost_range = int(ability_data["boost_power_divergence_range"])
    c_boost_ability_summary = ""
    if c_ability_boost_type != 0:
        assert c_ability_boost_range == 0 or c_ability_boost_range == 1
        c_ability_boost_range_str = "自身" if c_ability_boost_range == 0 else "我方"
        c_ability_boost_type_str = BuffEffectCategory[c_ability_boost_type]
        c_boost_ability_summary = (
            c_ability_boost_range_str + "、" + c_ability_boost_type_str
        )

    # 擦弹能力效果
    c_purge_ability_summary = ""
    c_ability_purge_type = int(ability_data["purge_barrier_diffusion_type"])
    c_ability_purge_range = int(ability_data["purge_barrier_diffusion_range"])
    if c_ability_purge_type != 0:
        assert c_ability_purge_range == 0 or c_ability_purge_range == 1
        c_ability_purge_range_str = "自身" if c_ability_purge_range == 0 else "我方"
        c_ability_purge_type_str = BuffEffectCategory[c_ability_purge_type]
        c_purge_ability_summary = (
            c_ability_purge_range_str + "、" + c_ability_purge_type_str
        )

    # 特性
    characteristic_data = characteristic_datas[int(unit_data["characteristic_id"])]
    c_characteristic_1_name = characteristic_data["characteristic1_name"]
    c_characteristic_1_effect = characteristic_data["characteristic1_description"]
    c_characteristic_1_icon = characteristic_data["characteristic1_icon_filename"]
    c_characteristic_2_name = characteristic_data["characteristic2_name"]
    c_characteristic_2_effect = characteristic_data["characteristic2_description"]
    c_characteristic_2_icon = characteristic_data["characteristic2_icon_filename"]
    c_characteristic_3_name = characteristic_data["characteristic3_name"]
    c_characteristic_3_effect = characteristic_data["characteristic3_description"]
    c_characteristic_3_icon = characteristic_data["characteristic3_icon_filename"]
    c_exchange_name = characteristic_data["trust_characteristic_name"]
    c_exchange_effect = characteristic_data["trust_characteristic_description"]

    # 主动技能
    c_skill_ids = [int(unit_data["skill" + str(i) + "_id"]) for i in range(1, 4)]
    c_skill_names = []
    c_skill_icons = []
    c_skill_descriptions = []
    c_skill_effects_ids = []
    c_skill_turns = []
    for c_skill_id in c_skill_ids:
        skill_data = skill_datas[c_skill_id]
        c_skill_names.append(skill_data["name"])
        c_skill_icons.append(skill_data["icon_filename"])
        c_skill_descriptions.append(skill_data["description"])
        c_skill_effects_ids.append(
            [int(skill_data["effect" + str(i) + "_id"]) for i in range(1, 4)]
        )
        c_skill_turns.append(
            [int(skill_data["level" + str(i) + "_turn"]) for i in range(1, 11)]
        )
    c_skill_effects = []
    c_skill_simples = []
    skill_index = 0
    for c_skill_effect_ids in c_skill_effects_ids:
        skill_index += 1
        c_skill_effect = ""
        c_skill_simple = []
        effect_index = 0
        for c_skill_effect_id in c_skill_effect_ids:
            effect_index += 1
            if c_skill_effect_id != 0:
                c_skill_effect_data = skill_effect_datas[c_skill_effect_id]
                effect_summary = c_skill_effect_data["description"]
                c_skill_effect_value = str(c_skill_effect_data["level10_value"])
                c_skill_effect_success_rate = str(
                    c_skill_effect_data["level10_success_rate"]
                )
                c_skill_effect_add_value = str(c_skill_effect_data["level10_add_value"])
                c_skill_effect_type = str(c_skill_effect_data["type"])
                if c_skill_effect_type == "5":
                    c_skill_effect_value = str(int(c_skill_effect_value) / 20)
                effect_summary = effect_summary.replace("{0}", c_skill_effect_value)
                effect_summary = effect_summary.replace(
                    "{1}", c_skill_effect_success_rate
                )
                effect_summary = effect_summary.replace("{2}", c_skill_effect_add_value)
                effect_summary = effect_summary.replace("[发生率0%追加效果+0]", "")
                effect_summary = effect_summary.replace("[发生率0%追加效果+1]", "")
                effect_summary = effect_summary.replace(
                    "<color=", "<font color="
                ).replace("</color>", "</font>")
                c_skill_effect = c_skill_effect + effect_summary + "<br>"
                c_skill_simple.append(
                    simplify_skill_effect(
                        c_id,
                        skill_index,
                        effect_index,
                        c_skill_effect,
                        c_skill_effect_id,
                    )
                )
        c_skill_effect = c_skill_effect[:-4]
        c_skill_effects.append(c_skill_effect)
        c_skill_simples.append(c_skill_simple)

    characters = OrderedDict()
    characters["实装日期"] = c_date
    generate_costume_info(characters, c_id)
    characters["外号"] = ""
    characters["评测"] = ""
    characters["人物编号"] = c_id
    characters["人物名称"] = c_name
    characters["称号"] = c_title
    characters["简称"] = c_name_short
    characters["泛异记号"] = c_mark
    characters["世界群"] = c_symbol_title
    characters["世界群介绍"] = c_symbol_description
    characters["页面名"] = page_name
    characters["泛异记号世界团"] = c_mark[0]
    characters["获取时台词"] = c_drop_text
    characters["式"] = c_role.replace("式", "")
    characters["检索用稀有度"] = c_rare
    characters["稀有度"] = RareCategory[c_rare]
    characters["角色BGM"] = c_bgm
    characters["种族"] = c_race
    characters["生命"] = c_lp
    characters["阳攻"] = c_yang_atk
    characters["阳防"] = c_yang_def
    characters["阴攻"] = c_yin_atk
    characters["阴防"] = c_yin_def
    characters["速度"] = c_speed
    characters["气质名称"] = c_resist_name
    characters["气质解说"] = c_resist_description
    characters["日抗性"] = c_resist_ri
    characters["月抗性"] = c_resist_yue
    characters["火抗性"] = c_resist_huo
    characters["水抗性"] = c_resist_shui
    characters["木抗性"] = c_resist_mu
    characters["金抗性"] = c_resist_jin
    characters["土抗性"] = c_resist_tu
    characters["星抗性"] = c_resist_xing
    characters["免疫异常"] = get_abnormal_set(1)
    characters["无效异常"] = get_abnormal_set(2)
    characters["反弹异常"] = get_abnormal_set(3)
    characters["回血异常"] = get_abnormal_set(4)
    characters["回灵异常"] = get_abnormal_set(5)
    characters["激昂异常"] = get_abnormal_set(6)
    characters["硬化异常"] = get_abnormal_set(7)
    characters["速力异常"] = get_abnormal_set(8)
    characters["能力名称"] = c_ability_name
    characters["能力解说"] = c_ability_description
    characters["能力效果"] = c_ability_effect_summary
    characters["强化能力效果"] = c_boost_ability_summary
    characters["擦弹能力效果"] = c_purge_ability_summary
    characters["特性1名称"] = c_characteristic_1_name
    characters["特性1效果"] = c_characteristic_1_effect.replace(
        "<color=", "<font color="
    ).replace("</color>", "</font>")
    characters["特性1图标"] = c_characteristic_1_icon
    characters["特性2名称"] = c_characteristic_2_name
    characters["特性2效果"] = c_characteristic_2_effect.replace(
        "<color=", "<font color="
    ).replace("</color>", "</font>")
    characters["特性2图标"] = c_characteristic_2_icon
    characters["特性3名称"] = c_characteristic_3_name
    characters["特性3效果"] = c_characteristic_3_effect.replace(
        "<color=", "<font color="
    ).replace("</color>", "</font>")
    characters["特性3图标"] = c_characteristic_3_icon
    characters["连携名称"] = c_exchange_name
    characters["连携效果"] = c_exchange_effect.replace("<color=", "<font color=").replace(
        "</color>", "</font>"
    )
    characters["技能1名称"] = c_skill_names[0]
    characters["技能1图标"] = c_skill_icons[0]
    characters["技能1cd"] = c_skill_turns[0][9]
    characters["技能1效果"] = c_skill_effects[0]
    characters["技能1描述"] = c_skill_descriptions[0]
    characters["技能2名称"] = c_skill_names[1]
    characters["技能2图标"] = c_skill_icons[1]
    characters["技能2cd"] = c_skill_turns[1][9]
    characters["技能2效果"] = c_skill_effects[1]
    characters["技能2描述"] = c_skill_descriptions[1]
    characters["技能3名称"] = c_skill_names[2]
    characters["技能3图标"] = c_skill_icons[2]
    characters["技能3cd"] = c_skill_turns[2][9]
    characters["技能3效果"] = c_skill_effects[2]
    characters["技能3描述"] = c_skill_descriptions[2]
    characters["技能1概括"] = "、".join(c_skill_simples[0])
    characters["技能2概括"] = "、".join(c_skill_simples[1])
    characters["技能3概括"] = "、".join(c_skill_simples[2])

    tegongs = []
    # 集中与扩散
    shot_ids = [int(unit_data["shot1_id"]), int(unit_data["shot2_id"])]
    shot_abnormal_breaks = [None, [], []]
    shot_index = 0
    for shot_id in shot_ids:
        shot_index += 1
        shot_data = shot_datas[shot_id]
        shot_type = "扩散" if shot_index == 1 else "集中"
        shot_name = shot_data["name"]
        shot_description = shot_data["description"]
        shot_range = "单体" if int(shot_data["magazine0_bullet_range"]) == 1 else "群体"
        shot_power_up_rate = str(int(shot_data["phantasm_power_up_rate"]) / 5) + "%"
        shot_boost_counts = [
            0,
            int(shot_data["magazine1_boost_count"]),
            int(shot_data["magazine2_boost_count"]),
            int(shot_data["magazine3_boost_count"]),
            int(shot_data["magazine4_boost_count"]),
            int(shot_data["magazine5_boost_count"]),
        ]
        shot_power_rate = [
            int(shot_data["shot_level" + str(i) + "_power_rate"]) for i in range(6)
        ]
        characters[shot_type + "名称"] = shot_name
        characters[shot_type + "描述"] = shot_description
        characters[shot_type + "范围"] = shot_range
        characters[shot_type + "等级补正1"] = shot_power_rate[0]
        characters[shot_type + "等级补正2"] = shot_power_rate[1]
        characters[shot_type + "等级补正3"] = shot_power_rate[2]
        characters[shot_type + "等级补正4"] = shot_power_rate[3]
        characters[shot_type + "等级补正5"] = shot_power_rate[4]
        characters[shot_type + "等级补正6"] = shot_power_rate[5]

        shot_bullet_ids = [
            int(shot_data["magazine" + str(i) + "_bullet_id"]) for i in range(6)
        ]
        shot_bullet_names = []
        shot_bullet_effect_icons = []
        shot_bullet_values = [
            int(shot_data["magazine" + str(i) + "_bullet_value"]) for i in range(6)
        ]
        shot_bullet_yinyangs = []
        shot_bullet_elements = []
        shot_bullet_types = []
        shot_bullet_powers = [
            int(shot_data["magazine" + str(i) + "_bullet_power_rate"]) for i in range(6)
        ]
        shot_bullet_powers = [x / 100 for x in shot_bullet_powers]
        shot_bullet_hit_rates = []
        shot_bullet_criticals = []
        shot_bullet_effects = []
        for i in range(6):
            bullet_id = shot_bullet_ids[i]
            bullet_data = bullet_datas[bullet_id]
            shot_bullet_names.append(bullet_data["name"])
            bullet_yinyang = "阴" if int(bullet_data["type"]) == 0 else "阳"
            shot_bullet_yinyangs.append(bullet_yinyang)
            shot_bullet_elements.append(Elements[int(bullet_data["element"])])
            shot_bullet_types.append(BulletCategory[int(bullet_data["category"])])
            shot_bullet_hit_rates.append(str(bullet_data["hit"]) + "%")
            shot_bullet_criticals.append(str(bullet_data["critical"]) + "%")
            addon_ids = [
                int(bullet_data["bullet" + str(i) + "_addon_id"]) for i in range(1, 4)
            ]
            b_addon_name = []  # 词条
            b_addon_description = []
            b_addon_value = [
                int(bullet_data["bullet" + str(i) + "_addon_value"])
                for i in range(1, 4)
            ]  # 只有4:硬质、5:斩裂有有效值
            for addon_id in addon_ids:
                if addon_id == 0:
                    b_addon_name.append("")
                    b_addon_description.append("")
                else:
                    bullet_addon_data = bullet_addon_datas[addon_id]
                    b_addon_name.append(bullet_addon_data["name"])
                    b_addon_description.append(bullet_addon_data["description"])
                    if addon_id >= 12 and addon_id <= 16:
                        shot_abnormal_breaks[shot_index].append(
                            AbnormalBreakCategory[addon_id]
                        )
            bullet_race_ids = (
                bullet_critical_races[bullet_id]
                if bullet_id in bullet_critical_races
                else []
            )
            b_race = []  # 特攻
            for bullet_race_id in bullet_race_ids:
                race_data = race_datas[bullet_race_id]
                b_race.append(race_data["name"])
                tegongs.append(race_data["name"])
            effect_ids = [
                int(bullet_data["bullet" + str(i) + "_extraeffect_id"])
                for i in range(1, 4)
            ]
            b_effect_rate = [
                int(bullet_data["bullet" + str(i) + "_extraeffect_success_rate"])
                for i in range(1, 4)
            ]
            b_effect_name = []  # 效果名
            b_effect_description = []  # 效果描述
            for effect_id in effect_ids:
                if effect_id == 0:
                    b_effect_name.append("")
                    b_effect_description.append("")
                else:
                    bullet_extra_effect_data = bullet_extra_effect_datas[effect_id]
                    b_effect_name.append(bullet_extra_effect_data["name"])
                    b_effect_description.append(bullet_extra_effect_data["description"])
            bullet_effect = ""
            effect_icon = ""
            if len(b_race) > 0:
                effect_icon += file_maker("段落 特攻.png", effect_icon_size)
                for j in range(len(b_race)):
                    bullet_effect += file_maker("段落 特攻.png", effect_icon_size)
                    bullet_effect += tegong_maker(b_race[j])
                    bullet_effect += "<br>"
            for j in range(3):
                if b_addon_name[j] != "":
                    effect_icon += file_maker(
                        "段落 " + b_addon_name[j] + ".png", effect_icon_size
                    )
                    bullet_effect += file_maker(
                        "段落 " + b_addon_name[j] + ".png", effect_icon_size
                    )
                    if addon_ids[j] == 4:
                        bullet_effect += (
                            "防御力的" + str(b_addon_value[j]) + "%转化为攻击力加成后造成伤害"
                        )
                    elif addon_ids[j] == 5:
                        bullet_effect += (
                            "速度的" + str(b_addon_value[j]) + "%转化为攻击力加成后造成伤害"
                        )
                    else:
                        bullet_effect += bullet_effect_maker(
                            b_addon_name[j], -1, b_addon_description[j]
                        )
                    bullet_effect += "<br>"
            for j in range(3):
                if b_effect_name[j] != "":
                    if "▼" in b_effect_name[j] or "△" in b_effect_name[j]:
                        effect_icon += (
                            file_maker(
                                "效果 " + b_effect_name[j] + ".png", effect_icon_size
                            )
                            .replace("▼", " 下降")
                            .replace("△", " 上升")
                        )
                        bullet_effect += (
                            file_maker(
                                "效果 " + b_effect_name[j] + ".png", effect_icon_size
                            )
                            .replace("▼", " 下降")
                            .replace("△", " 上升")
                        )
                    else:
                        effect_icon += file_maker(
                            "段落 " + b_effect_name[j] + ".png", effect_icon_size
                        )
                        bullet_effect += file_maker(
                            "段落 " + b_effect_name[j] + ".png", effect_icon_size
                        )
                    bullet_effect += bullet_effect_maker(
                        b_effect_name[j], b_effect_rate[j], b_effect_description[j]
                    )
                    bullet_effect += "<br>"
            effect_icon = effect_icon.replace("△", " 上升")
            bullet_effect = bullet_effect.replace("△", " 上升")
            shot_bullet_effects.append(bullet_effect)
            shot_bullet_effect_icons.append(effect_icon)
            characters[shot_type + str(i + 1) + "名称"] = shot_bullet_names[i]
            characters[shot_type + str(i + 1) + "效果图标"] = shot_bullet_effect_icons[i]
            characters[shot_type + str(i + 1) + "数量"] = shot_bullet_values[i]
            characters[shot_type + str(i + 1) + "阴阳"] = shot_bullet_yinyangs[i]
            characters[shot_type + str(i + 1) + "属性"] = shot_bullet_elements[i]
            characters[shot_type + str(i + 1) + "弹种"] = shot_bullet_types[i]
            characters[shot_type + str(i + 1) + "威力"] = shot_bullet_powers[i]
            characters[shot_type + str(i + 1) + "命中率"] = shot_bullet_hit_rates[i]
            characters[shot_type + str(i + 1) + "会心率"] = shot_bullet_criticals[i]
            characters[shot_type + str(i + 1) + "回灵率"] = shot_power_up_rate
            characters[shot_type + str(i + 1) + "具体效果"] = shot_bullet_effects[i]
            characters[shot_type + str(i + 1) + "所需灵力"] = shot_boost_counts[i]

    # 符卡
    spell_ids = [
        int(unit_data["spellcard1_id"]),
        int(unit_data["spellcard2_id"]),
        int(unit_data["spellcard5_id"]),
    ]
    spell_index = 0
    spell_abnormal_breaks = [None, [], [], []]
    for spell_id in spell_ids:
        spell_index += 1
        spell_card_data = spell_card_datas[spell_id]
        spell_type = "终符" if spell_index == 3 else str(spell_index) + "符"
        spell_name = spell_card_data["name"]
        spell_description = spell_card_data["description"]
        spell_range = (
            "单体" if int(spell_card_data["magazine0_bullet_range"]) == 1 else "群体"
        )
        spell_power_up_rate = (
            str(int(spell_card_data["phantasm_power_up_rate"]) / 5) + "%"
        )
        spell_boost_counts = [
            0,
            int(spell_card_data["magazine1_boost_count"]),
            int(spell_card_data["magazine2_boost_count"]),
            int(spell_card_data["magazine3_boost_count"]),
            int(spell_card_data["magazine4_boost_count"]),
            int(spell_card_data["magazine5_boost_count"]),
        ]
        spell_effect_ids = [
            int(spell_card_data["spellcard_skill" + str(i) + "_effect_id"])
            for i in range(1, 6)
        ]
        spell_effect_level_types = [
            int(spell_card_data["spellcard_skill" + str(i) + "_level_type"])
            for i in range(1, 6)
        ]  # 效果类型：1固定，2随星级变换，3随灵力强化变换
        spell_effect_timings = [
            int(spell_card_data["spellcard_skill" + str(i) + "_timing"])
            for i in range(1, 6)
        ]  # 效果时机：1攻击前，2攻击后
        spell_power_rate = [
            int(spell_card_data["shot_level" + str(i) + "_power_rate"])
            for i in range(1, 6)
        ]
        effect_before_count = 1
        effect_after_count = 1
        effect_count = 0
        for effect_index in range(1, 6):
            characters[spell_type + "攻击前效果" + str(effect_index) + "类型"] = ""
            characters[spell_type + "攻击前效果" + str(effect_index) + "图标"] = ""
            characters[spell_type + "攻击后效果" + str(effect_index) + "类型"] = ""
            characters[spell_type + "攻击后效果" + str(effect_index) + "图标"] = ""
            for effect_level in range(1, 6):
                characters[
                    spell_type + "攻击前效果" + str(effect_index) + "等级" + str(effect_level)
                ] = ""
                characters[
                    spell_type + "攻击后效果" + str(effect_index) + "等级" + str(effect_level)
                ] = ""
        for spell_effect_id in spell_effect_ids:
            if spell_effect_id == 0:
                break
            spell_effect_data = skill_effect_datas[spell_effect_id]
            spell_effect_description = spell_effect_data["description"]  # 效果描述
            spell_effect_type = int(
                spell_effect_data["type"]
            )  # 效果类型，等于5时为灵力回复效果，需要除以20
            spell_effect_values = [
                int(spell_effect_data["level" + str(i) + "_value"])
                for i in range(1, 11)
            ]  # 效果值，共10个等级
            spell_effect_success_rates = [
                int(spell_effect_data["level" + str(i) + "_success_rate"])
                for i in range(1, 11)
            ]  # 概率提升效果的概率
            spell_effect_add_values = [
                int(spell_effect_data["level" + str(i) + "_add_value"])
                for i in range(1, 11)
            ]  # 概率提升效果的效果值
            spell_effect_icon_filename = spell_effect_data["icon_filename"]  # 图标名
            spell_effects = []
            for effect_flag in range(10):
                if spell_effect_type == 5:
                    spell_effect_values[effect_flag] /= 20
                effect_summary = spell_effect_description
                effect_summary = effect_summary.replace(
                    "{0}", str(spell_effect_values[effect_flag])
                )
                effect_summary = effect_summary.replace(
                    "{1}", str(spell_effect_success_rates[effect_flag])
                )
                effect_summary = effect_summary.replace(
                    "{2}", str(spell_effect_add_values[effect_flag])
                )
                effect_summary = effect_summary.replace("[发生率0%追加效果+0]", "")
                effect_summary = effect_summary.replace("[发生率0%追加效果+1]", "")
                effect_summary = effect_summary.replace(
                    "<color=", "<font color="
                ).replace("</color>", "</font>")
                spell_effects.append(effect_summary)
            if spell_effect_timings[effect_count] == 1:
                temp_name = spell_type + "攻击前效果" + str(effect_before_count)
                effect_before_count += 1
            else:
                temp_name = spell_type + "攻击后效果" + str(effect_after_count)
                effect_after_count += 1
            characters[temp_name + "图标"] = spell_effect_icon_filename
            if spell_effect_level_types[effect_count] == 1:
                characters[temp_name + "类型"] = "固定"
                characters[temp_name + "等级1"] = spell_effects[0]
                characters[temp_name + "等级2"] = spell_effects[0]
                characters[temp_name + "等级3"] = spell_effects[0]
                characters[temp_name + "等级4"] = spell_effects[0]
                characters[temp_name + "等级5"] = spell_effects[0]
            elif spell_effect_level_types[effect_count] == 2:
                characters[temp_name + "类型"] = "星级相关"
                characters[temp_name + "等级1"] = spell_effects[1]
                characters[temp_name + "等级2"] = spell_effects[3]
                characters[temp_name + "等级3"] = spell_effects[5]
                characters[temp_name + "等级4"] = spell_effects[7]
                characters[temp_name + "等级5"] = spell_effects[9]
            else:
                characters[temp_name + "类型"] = "灵力相关"
                characters[temp_name + "等级1"] = spell_effects[0]
                characters[temp_name + "等级2"] = spell_effects[3]
                characters[temp_name + "等级3"] = spell_effects[6]
                characters[temp_name + "等级4"] = spell_effects[9]
                characters[temp_name + "等级5"] = spell_effects[9]
            effect_count += 1

        characters[spell_type + "名称"] = spell_name
        characters[spell_type + "描述"] = spell_description
        characters[spell_type + "范围"] = spell_range
        characters[spell_type + "等级补正1"] = spell_power_rate[0]
        characters[spell_type + "等级补正2"] = spell_power_rate[1]
        characters[spell_type + "等级补正3"] = spell_power_rate[2]
        characters[spell_type + "等级补正4"] = spell_power_rate[3]
        characters[spell_type + "等级补正5"] = spell_power_rate[4]

        spell_bullet_ids = [
            int(spell_card_data["magazine" + str(i) + "_bullet_id"]) for i in range(6)
        ]
        spell_bullet_names = []
        spell_bullet_effect_icons = []
        spell_bullet_values = [
            int(spell_card_data["magazine" + str(i) + "_bullet_value"])
            for i in range(6)
        ]
        spell_bullet_yinyangs = []
        spell_bullet_elements = []
        spell_bullet_types = []
        spell_bullet_powers = [
            int(spell_card_data["magazine" + str(i) + "_bullet_power_rate"])
            for i in range(6)
        ]
        spell_bullet_powers = [x / 100 for x in spell_bullet_powers]
        spell_bullet_hit_rates = []
        spell_bullet_criticals = []
        spell_bullet_effects = []
        for i in range(6):
            bullet_id = spell_bullet_ids[i]
            if bullet_id == 0:
                break
            bullet_data = bullet_datas[bullet_id]
            spell_bullet_names.append(bullet_data["name"])
            bullet_yinyang = "阴" if int(bullet_data["type"]) == 0 else "阳"
            spell_bullet_yinyangs.append(bullet_yinyang)
            spell_bullet_elements.append(Elements[int(bullet_data["element"])])
            spell_bullet_types.append(BulletCategory[int(bullet_data["category"])])
            spell_bullet_hit_rates.append(str(bullet_data["hit"]) + "%")
            spell_bullet_criticals.append(str(bullet_data["critical"]) + "%")
            addon_ids = [
                int(bullet_data["bullet" + str(i) + "_addon_id"]) for i in range(1, 4)
            ]
            b_addon_name = []  # 词条
            b_addon_description = []
            b_addon_value = [
                int(bullet_data["bullet" + str(i) + "_addon_value"])
                for i in range(1, 4)
            ]  # 只有4:硬质、5:斩裂有有效值
            for addon_id in addon_ids:
                if addon_id == 0:
                    b_addon_name.append("")
                    b_addon_description.append("")
                else:
                    bullet_addon_data = bullet_addon_datas[addon_id]
                    b_addon_name.append(bullet_addon_data["name"])
                    b_addon_description.append(bullet_addon_data["description"])
                    if addon_id >= 12 and addon_id <= 16:
                        spell_abnormal_breaks[spell_index].append(
                            AbnormalBreakCategory[addon_id]
                        )
            bullet_race_ids = (
                bullet_critical_races[bullet_id]
                if bullet_id in bullet_critical_races
                else []
            )
            b_race = []  # 特攻
            for bullet_race_id in bullet_race_ids:
                race_data = race_datas[bullet_race_id]
                b_race.append(race_data["name"])
                tegongs.append(race_data["name"])
            effect_ids = [
                int(bullet_data["bullet" + str(i) + "_extraeffect_id"])
                for i in range(1, 4)
            ]
            b_effect_rate = [
                int(bullet_data["bullet" + str(i) + "_extraeffect_success_rate"])
                for i in range(1, 4)
            ]
            b_effect_name = []  # 效果名
            b_effect_description = []  # 效果描述
            for effect_id in effect_ids:
                if effect_id == 0:
                    b_effect_name.append("")
                    b_effect_description.append("")
                else:
                    bullet_extra_effect_data = bullet_extra_effect_datas[effect_id]
                    b_effect_name.append(bullet_extra_effect_data["name"])
                    b_effect_description.append(bullet_extra_effect_data["description"])
            bullet_effect = ""
            effect_icon = ""
            if len(b_race) > 0:
                effect_icon += file_maker("段落 特攻.png", effect_icon_size)
                for j in range(len(b_race)):
                    bullet_effect += file_maker("段落 特攻.png", effect_icon_size)
                    bullet_effect += tegong_maker(b_race[j])
                    bullet_effect += "<br>"
            for j in range(3):
                if b_addon_name[j] != "":
                    effect_icon += file_maker(
                        "段落 " + b_addon_name[j] + ".png", effect_icon_size
                    )
                    bullet_effect += file_maker(
                        "段落 " + b_addon_name[j] + ".png", effect_icon_size
                    )
                    if addon_ids[j] == 4:
                        bullet_effect += (
                            "防御力的" + str(b_addon_value[j]) + "%转化为攻击力加成后造成伤害"
                        )
                    elif addon_ids[j] == 5:
                        bullet_effect += (
                            "速度的" + str(b_addon_value[j]) + "%转化为攻击力加成后造成伤害"
                        )
                    else:
                        bullet_effect += bullet_effect_maker(
                            b_addon_name[j], -1, b_addon_description[j]
                        )
                    bullet_effect += "<br>"
            for j in range(3):
                if b_effect_name[j] != "":
                    if "▼" in b_effect_name[j] or "△" in b_effect_name[j]:
                        effect_icon += (
                            file_maker(
                                "效果 " + b_effect_name[j] + ".png", effect_icon_size
                            )
                            .replace("▼", " 下降")
                            .replace("△", " 上升")
                        )
                        bullet_effect += (
                            file_maker(
                                "效果 " + b_effect_name[j] + ".png", effect_icon_size
                            )
                            .replace("▼", " 下降")
                            .replace("△", " 上升")
                        )
                    else:
                        effect_icon += file_maker(
                            "段落 " + b_effect_name[j] + ".png", effect_icon_size
                        )
                        bullet_effect += file_maker(
                            "段落 " + b_effect_name[j] + ".png", effect_icon_size
                        )
                    bullet_effect += bullet_effect_maker(
                        b_effect_name[j], b_effect_rate[j], b_effect_description[j]
                    )
                    bullet_effect += "<br>"
            spell_bullet_effects.append(bullet_effect)
            spell_bullet_effect_icons.append(effect_icon)
            characters[spell_type + str(i + 1) + "名称"] = spell_bullet_names[i]
            characters[spell_type + str(i + 1) + "效果图标"] = spell_bullet_effect_icons[i]
            characters[spell_type + str(i + 1) + "数量"] = spell_bullet_values[i]
            characters[spell_type + str(i + 1) + "阴阳"] = spell_bullet_yinyangs[i]
            characters[spell_type + str(i + 1) + "属性"] = spell_bullet_elements[i]
            characters[spell_type + str(i + 1) + "弹种"] = spell_bullet_types[i]
            characters[spell_type + str(i + 1) + "威力"] = spell_bullet_powers[i]
            characters[spell_type + str(i + 1) + "命中率"] = spell_bullet_hit_rates[i]
            characters[spell_type + str(i + 1) + "会心率"] = spell_bullet_criticals[i]
            characters[spell_type + str(i + 1) + "回灵率"] = spell_power_up_rate
            characters[spell_type + str(i + 1) + "具体效果"] = spell_bullet_effects[i]
            characters[spell_type + str(i + 1) + "所需灵力"] = spell_boost_counts[i]

    generate_time_duration(characters, c_id)
    characters["特攻"] = "、".join(sorted(list(set(tegongs))))
    characters["扩散破异常"] = "、".join(sorted(list(set(shot_abnormal_breaks[1]))))
    characters["集中破异常"] = "、".join(sorted(list(set(shot_abnormal_breaks[2]))))
    characters["1符破异常"] = "、".join(sorted(list(set(spell_abnormal_breaks[1]))))
    characters["2符破异常"] = "、".join(sorted(list(set(spell_abnormal_breaks[2]))))
    characters["终符破异常"] = "、".join(sorted(list(set(spell_abnormal_breaks[3]))))
    generate_friendship_characters(characters, c_id)
    generate_overall_elements(characters, c_id)
    generate_voice(characters, c_id)
    generate_cv_info(characters, c_id)
    generate_rank_promote(characters, c_id)
    generate_hit_check_order(characters, c_id)
    fixup_return_line(characters)

    assert page_name not in characters_json
    characters_json[page_name] = characters

with open(
    os.path.join("./tracking_files/", "characters_wikidata.json"), "w", encoding="utf-8"
) as f:
    json_string = json.dumps(
        characters_json, ensure_ascii=False, separators=(",\n", ": ")
    )
    f.write(json_string)
