#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
"""

import csv
import json
import os
import re
import shutil
import sys


dir_to_jsons = sys.argv[1]
dir_to_data = sys.argv[2]

if os.path.exists(os.path.join("./tracking_files", "catagory_pages.json")):
    shutil.copyfile(
        os.path.join("./tracking_files", "catagory_pages.json"),
        os.path.join("./local_files", "old_catagory_pages.json"),
    )
if os.path.exists(os.path.join("./tracking_files", "chapter_pages.json")):
    shutil.copyfile(
        os.path.join("./tracking_files", "chapter_pages.json"),
        os.path.join("./local_files", "old_chapter_pages.json"),
    )
if os.path.exists(os.path.join("./tracking_files", "section_pages.json")):
    shutil.copyfile(
        os.path.join("./tracking_files", "section_pages.json"),
        os.path.join("./local_files", "old_section_pages.json"),
    )
if os.path.exists(os.path.join("./tracking_files", "comic_pages.json")):
    shutil.copyfile(
        os.path.join("./tracking_files", "comic_pages.json"),
        os.path.join("./local_files", "old_comic_pages.json"),
    )


def wrap(text: str) -> str:
    text = text.replace("\n", "<br>")
    text = text.replace("~", "～")
    text = text.replace("<ret>", "")
    if "\u001b" in text:
        text = text.replace("\u001bh", "(主角名)")
        if "\u001b" in text:
            text = re.sub(r"\u001b[0-9a-z]+", "", text)
        assert "\u001b" not in text
    return text


def title_wrapper(title: str) -> str:
    return title.replace("[", "【").replace("]", "】")


def subtitle_wrapper(subtitle: str) -> str:
    if re.search(r"^\s*$", subtitle) or subtitle == "(empty)":
        return ""
    return "【" + subtitle + "】"


def get_ucid(order: dict[str, dict]) -> str:
    if "m_ucid" in order:
        return str(order["m_ucid"])
    assert order["m_cstmid"] < 100
    return str(order["m_unitid"]) + str(order["m_cstmid"]).zfill(2)


def process_order(
    order_name: str,
    order: dict[str, dict],
    unit_names: dict[str, str],
    env: dict[str, any],
    used_image_set: set[str],
    bgm_table: dict[int, str],
    costume_table: dict[int, tuple[str, str]],
):
    if order_name == "BattleOrder":
        if env.get("last_valid_order", "") == "BattleOrder":
            return ""
        return "{{剧本模板事件|文本=姬烈的战斗。。。}}"
    elif order_name == "ButtonOrder":
        return "{{剧本模板玩家选项|选项1=" + wrap(order["m_strbtn"]) + "|选项2=|选项3=}}"
    elif order_name == "IntroUnitInOrder":
        ucid = get_ucid(order)
        unit_name, name = costume_table[int(ucid)]
        return (
            "{{剧本模板事件|图片=CH"
            + ucid
            + ".png|文本=介绍角色：\n"
            + unit_name
            + "\n【"
            + name
            + "】}}"
        )
    elif order_name == "LoadBGOrder":
        bg_file = order["m_name"]
        if "last_bg_file" in env and env["last_bg_file"] == bg_file:
            # no need to do anything if the bg is not actually changed
            return ""
        env["last_bg_file"] = bg_file
        if bg_file.lower().startswith("comic/bg/"):
            used_image_set.add("1 " + bg_file)
            bg_file = "CBG" + bg_file[9:]
        elif bg_file.lower().startswith("bg_resource_"):
            used_image_set.add("2 " + bg_file)
            bg_file = "CBG" + bg_file[12:]
        elif bg_file.lower().startswith("event"):
            used_image_set.add("3 " + bg_file)
            bg_file = os.path.basename(bg_file)
            assert bg_file.endswith(".png")
            bg_file = "EBG" + bg_file
        elif bg_file.lower().startswith("main"):
            used_image_set.add("4 " + bg_file)
            bg_file = os.path.basename(bg_file)
            assert bg_file.endswith(".png")
            bg_file = "MBG" + bg_file
        else:
            raise Exception("unhandled bg file path")
        return "{{剧本模板事件|图片=" + bg_file + "|文本=【切换背景】}}"
    elif order_name == "LoadItemOrder":
        return ""
    elif order_name == "LoadUnitOrder":
        ucid = get_ucid(order)
        unit_names[ucid] = order["m_name"]
        return ""
    elif order_name == "MessageOrder":
        return (
            "{{剧本模板对话框|角色名=" + order["m_name"] + "|文本=" + wrap(order["m_text"]) + "}}"
        )
    elif order_name == "PlayBGMOrder":
        env["bgm"] = True
        bgm_name = bgm_table[order["m_bgmid"]]
        return "{{剧本模板事件|文本=播放BGM：" + bgm_name + "}}"
    elif order_name == "RenameOrder":
        ucid = get_ucid(order)
        unit_names[str(order["m_ucid"])] = order["m_name"]
        return ""
    elif order_name == "SelectOrder":
        return (
            "{{剧本模板玩家选项|选项1="
            + wrap(order["m_strfst"])
            + "|选项2="
            + wrap(order["m_strsnd"])
            + "|选项3="
            + wrap(order["m_str3rd"])
            + "}}"
        )
    elif order_name == "StopBGMOrder":
        if "bgm" in env and env["bgm"] == True:
            env["bgm"] = False
            return "{{剧本模板事件|文本=BGM停止}}"
        else:
            return ""
    elif order_name == "TalkOrder":
        ucid = get_ucid(order)
        assert ucid in unit_names
        return (
            "{{剧本模板对话框|图片=S"
            + ucid
            + ".png|角色名="
            + unit_names[ucid]
            + "|文本="
            + wrap(order["m_text"])
            + "}}"
        )
    elif order_name in [
        "AnimeOrder",
        "BlurEffectOrder",
        "EffectColorOrder",
        "ElseOrder",
        "EndOrder",
        "FadeOrder",
        "FlipHorizontalUnitOrder",
        "ForeUnitOrder",
        "HeroOrder",
        "IfOrder",
        "InputNameOrder",
        "IntroGachaOrder",
        "IntroUnitOutOrder",
        "JumpUnitOrder",
        "LetterBoxOrder",
        "LoadCameraEffect",
        "LoadEffectOrder",
        "LoadItemOrder",
        "LoadRuleOrder",
        "MicroSkipOrder",
        "MoveBGOrder",
        "MoveCameraOrder",
        "MoveItemOrder",
        "MoveUnitOrder",
        "NoiseUnitOrder",
        "PlayEffectOrder",
        "PlaySEOrder",
        "PositUnitOrder",
        "PostEffectOrder",
        "RewindOrder",
        "RuleFadeOrder",
        "ScaleBGOrder",
        "ScaleItemOrder",
        "ScaleUnitOrder",
        "ShakeViewOrder",
        "ShowBGOrder",
        "ShowIconOrder",
        "ShowItemOrder",
        "ShowUIOrder",
        "ShowUnitOrder",
        "ShowWindowOrder",
        "SolidInOrder",
        "SolidOutOrder",
        "SplashOrder",
        "StopEffectOrder",
        "StopSEOrder",
        "SwayItemOrder",
        "SwayStopItemOrder",
        "SwayStopOrder",
        "SwayUnitOrder",
        "TintUnitOrder",
        "WaitOrder",
        "ZoomCameraOrder",
    ]:
        # these orders are currently not handled
        return ""
    else:
        raise Exception("order name:", order_name, "is not handled")


def get_file_catagory(json_file_name):
    json_file_name = json_file_name.lower()
    if json_file_name.startswith("another"):
        return "秘封"
    elif json_file_name.startswith("characterquest"):
        return "衣装解放"
    elif json_file_name.startswith("event"):
        return "活动"
    elif json_file_name.startswith("main"):
        return "主线"
    elif json_file_name.startswith("relicquest"):
        return "记忆遗迹"
    elif json_file_name.startswith("tower"):
        return "红魔塔"
    elif json_file_name.startswith("yukkuri"):
        return "油库里"
    else:
        return "其他"


def extract_comic_filepath(comic_filepath: str) -> str:
    assert comic_filepath.endswith(".asset")
    return comic_filepath[:-6]


# process data tables
bgm_table: dict[int, str] = {}
with open(os.path.join(dir_to_data, "BgmTable.csv")) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        bgm_table[int(row["id"])] = row["name"] + "【原曲：" + row["original_name"] + "】"
if 1065 not in bgm_table:
    bgm_table[1065] = "某惊悚的BGM，半夜别听（bushi"
if 1066 not in bgm_table:
    bgm_table[1066] = "？？？" + "【原曲：" + "なし" + "】"

unit_table: dict[int, str] = {}
unit_short_name: dict[int, str] = {}
with open(os.path.join(dir_to_data, "UnitTable.csv")) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        unit_table[int(row["id"])] = row["name"] + row["symbol_name"]
        unit_short_name[int(row["id"])] = row["short_name"] + row["symbol_name"]

costume_table: dict[int, tuple[str, str]] = {}
with open(os.path.join(dir_to_data, "CostumeTable.csv")) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        costume_table[int(row["id"])] = (unit_table[int(row["unit_id"])], row["name"])
assert 104102 not in costume_table
costume_table[104102] = ("森近霖之助", "海之家「香霖堂」")
assert 104103 not in costume_table
costume_table[104103] = ("森近霖之助", "秘汤特产「香霖堂」")
assert 307201 not in costume_table
costume_table[307201] = ("上白泽慧音", "吞食历史")
# assert 201801 not in costume_table
costume_table[201801] = ("八意永琳", "绯苍的贤帝")
assert 190501 not in costume_table
costume_table[190501] = ("魅魔", "在久远的梦中听天由命的精神")
assert 193701 not in costume_table
costume_table[193701] = ("神绮", "魔界之神")
assert 803001 not in costume_table
costume_table[803001] = ("unknown", "unknown")
assert 700401 not in costume_table
costume_table[700401] = ("unknown", "unknown")
assert 1003201 not in costume_table
costume_table[1003201] = ("unknown", "unknown")

unit_speech_group_table: dict[int, list[str]] = {}
with open(os.path.join(dir_to_data, "UnitSpeechTable.csv")) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        unit_speech_group_table.setdefault(int(row["group_id"]), []).append(
            row["speech_text"]
        )
unit_speech_group_table[-2] = ["欢迎来到红魔塔"]

chapter_table: dict[int, str] = {}
chapter_kanban_info: dict[int, tuple[int, int]] = {}
with open(os.path.join(dir_to_data, "ChapterTable.csv")) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        if int(row["id"]) == 2085:  # 胶囊中的幻想乡改过名，没有意义
            continue
        if int(row["id"]) == 2087:  # 犯规解决代理人改过名，没有意义
            continue
        if int(row["id"]) == 2093:  # 黑衣的摄影师改过名，没有意义
            continue
        if int(row["id"]) == 2098:  # （去除冗余的后一个）弹幕小歌剧
            continue
        if int(row["id"]) == 2101:  # （去除冗余的后一个）幽现的狙击手
            continue
        if int(row["id"]) == 2104:  # （去除冗余的后一个）复苏的甜味
            continue
        if int(row["id"]) == 2109:  # （去除冗余的后一个）乐园的健康烹饪
            continue
        if int(row["id"]) == 2122:  # （去除冗余的后一个）启蛰的秘神游戏
            continue
        if int(row["id"]) == 2129:  # （去除冗余的后一个）三途河
            continue
        if int(row["id"]) == 2114:  # （去除冗余的后一个）一年又一年 弹幕家族
            continue
        if int(row["id"]) == 2118:  # （去除冗余的后一个）叛逆的微小幻想曲
            continue
        if int(row["id"]) == 2130:  # （去除冗余的后一个）博丽神社学院冒险谭 蕾米定向越野赛
            continue
        if int(row["id"]) == 2135:  # （去除冗余的后一个）野兽梦幻沙龙 欢迎来到！
            continue
        if int(row["id"]) == 2139:  # （去除冗余的后一个）
            continue
        if int(row["id"]) == 2144:  # （去除冗余的后一个）
            continue
        if int(row["id"]) == 2149:  # （去除冗余的后一个）
            continue
        if int(row["id"]) == 2152:  # （去除冗余的后一个）
            continue
        chapter_table[int(row["id"])] = title_wrapper(row["title"])
        chapter_kanban_info[int(row["id"])] = (
            int(row["costume_id"]),
            int(row["unit_speech_group_id"]),
        )

section_table: dict[int, tuple[int, str, str]] = {}
section_kanban_info: dict[int, tuple[int, int]] = {}
with open(os.path.join(dir_to_data, "SectionTable.csv")) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        if int(row["chapter_id"]) == 2085:
            continue
        if int(row["chapter_id"]) == 2087:
            continue
        if int(row["chapter_id"]) == 2093:
            continue
        if int(row["chapter_id"]) == 2098:
            continue
        if int(row["chapter_id"]) == 2101:
            continue
        if int(row["chapter_id"]) == 2104:
            continue
        if int(row["chapter_id"]) == 2109:
            continue
        if int(row["chapter_id"]) == 2122:
            continue
        if int(row["chapter_id"]) == 2129:
            continue
        if int(row["chapter_id"]) == 2114:
            continue
        if int(row["chapter_id"]) == 2118:
            continue
        if int(row["chapter_id"]) == 2130:
            continue
        if int(row["chapter_id"]) == 2135:
            continue
        if int(row["chapter_id"]) == 2139:
            continue
        if int(row["chapter_id"]) == 2144:
            continue
        if int(row["chapter_id"]) == 2149:
            continue
        if int(row["chapter_id"]) == 2152:
            continue
        section_table[int(row["id"])] = (
            int(row["chapter_id"]),
            title_wrapper(row["title"]),
            row["sub_title"],
        )
        section_kanban_info[int(row["id"])] = (
            int(row["costume_id"]),
            int(row["unit_speech_group_id"]),
        )

episode_table: dict[str, tuple[int, int, int, str, str]] = {}
episode_id_table: dict[int, str] = {}
with open(os.path.join(dir_to_data, "EpisodeTable.csv")) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        if int(row["chapter_id"]) == 2085:
            continue
        if int(row["chapter_id"]) == 2087:
            continue
        if int(row["chapter_id"]) == 2093:
            continue
        if int(row["chapter_id"]) == 2098:
            continue
        if int(row["chapter_id"]) == 2101:
            continue
        if int(row["chapter_id"]) == 2104:
            continue
        if int(row["chapter_id"]) == 2109:
            continue
        if int(row["chapter_id"]) == 2122:
            continue
        if int(row["chapter_id"]) == 2129:
            continue
        if int(row["chapter_id"]) == 2114:
            continue
        if int(row["chapter_id"]) == 2118:
            continue
        if int(row["chapter_id"]) == 2130:
            continue
        if int(row["chapter_id"]) == 2135:
            continue
        if int(row["chapter_id"]) == 2139:
            continue
        if int(row["chapter_id"]) == 2144:
            continue
        if int(row["chapter_id"]) == 2149:
            continue
        if int(row["chapter_id"]) == 2152:
            continue
        comic_filepath = "-".join(row["comic_filepath"].lower().split("/"))
        comic_filepath = extract_comic_filepath(comic_filepath)
        if not comic_filepath.startswith("daily"):
            assert (
                comic_filepath not in episode_table
                or episode_table[comic_filepath][3] == title_wrapper(row["title"])
                or episode_table[comic_filepath][4] == row["sub_title"]
            )
        episode_table[comic_filepath] = (
            int(row["chapter_id"]),
            int(row["section_id"]),
            int(row["id"]),
            title_wrapper(row["title"]),
            row["sub_title"],
        )
        episode_id_table[int(row["id"])] = comic_filepath

chara_chapter_table: dict[int, tuple[int, int]] = {}
with open(os.path.join(dir_to_data, "CharacterQuestChapterTable.csv")) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        chara_chapter_table[int(row["target_unit_id"])] = (
            int(row["costume_id"]),
            int(row["unit_speech_group_id"]),
        )

with open(os.path.join(dir_to_data, "CharacterEpisodeTable.csv")) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        comic_filepath = "-".join(row["comic_filepath"].lower().split("/"))
        comic_filepath = extract_comic_filepath(comic_filepath)
        if not comic_filepath.startswith("daily"):
            assert comic_filepath not in episode_table
        chapter_id = -1
        section_id = -(10000000 - int(row["unit_id"]))
        episode_id = -(10000000 - int(row["id"]))
        title = title_wrapper(unit_table[int(row["unit_id"])] + "的衣装解放")
        subtitle = ""
        section_table[section_id] = (chapter_id, title, subtitle)
        section_kanban_info[section_id] = chara_chapter_table[int(row["unit_id"])]
        episode_table[comic_filepath] = (
            chapter_id,
            section_id,
            episode_id,
            title,
            subtitle,
        )
        episode_id_table[episode_id] = comic_filepath

with open(os.path.join(dir_to_data, "TowerTable.csv")) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        comic_filepath = "-".join(row["comic_filepath"].lower().split("/"))
        comic_filepath = extract_comic_filepath(comic_filepath)
        if not comic_filepath.startswith("daily"):
            assert comic_filepath not in episode_table
        chapter_id = -2
        section_id = -(20000000 - int(row["floor"]))
        episode_id = -(20000000 - int(row["id"]))
        title = title_wrapper(row["title"])
        subtitle = row["comic_title"]
        section_table[section_id] = (chapter_id, title, subtitle)
        section_kanban_info[section_id] = (100303, -2)
        episode_table[comic_filepath] = (
            chapter_id,
            section_id,
            episode_id,
            title,
            subtitle,
        )
        episode_id_table[episode_id] = comic_filepath
section_table[-20000000] = (-2, "红魔塔序章", "红魔塔序章")
episode_table["tower-scarletdeviltower-floor0"] = (
    -2,
    -20000000,
    -20000000,
    "红魔塔序章",
    "红魔塔序章",
)
episode_id_table[-20000000] = "tower-scarletdeviltower-floor0"

relic_chapter_table: dict[int, tuple[int, int, int]] = {}
with open(os.path.join(dir_to_data, "RelicChapterTable.csv")) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        relic_chapter_table[int(row["id"])] = (
            int(row["costume_id"]),
            int(row["unit_speech_group_id"]),
            int(row["display_order"]),
        )

with open(os.path.join(dir_to_data, "RelicQuestTable.csv")) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        comic_filepath = "-".join(row["comic_filepath"].lower().split("/"))
        comic_filepath = extract_comic_filepath(comic_filepath)
        if not comic_filepath.startswith("daily"):
            assert comic_filepath not in episode_table
        relic_chapter_id = int(row["relic_chapter_id"])
        (
            kanban_costume_id,
            kanban_unit_speech_group_id,
            display_order,
        ) = relic_chapter_table[relic_chapter_id]
        display_order *= 100
        chapter_id = -3
        section_id = -(30000000 - display_order)
        episode_id = -(30000000 - int(row["id"]))
        title = title_wrapper(row["title"])
        subtitle = "相关角色: " + unit_table[int(row["id"][:-2])]
        while section_id in section_table:
            section_id += 1
        section_table[section_id] = (chapter_id, title, subtitle)
        section_kanban_info[section_id] = (
            kanban_costume_id,
            kanban_unit_speech_group_id,
        )
        episode_table[comic_filepath] = (
            chapter_id,
            section_id,
            episode_id,
            title,
            subtitle,
        )
        episode_id_table[episode_id] = comic_filepath

chapter_table[-1] = "衣装解放剧情"
chapter_table[-2] = "红魔塔剧情"
chapter_table[-3] = "记忆遗迹"
chapter_kanban_info[-2] = (100303, -2)

output_dir = os.path.join("./local_files", "comic_output")
if not os.path.exists(output_dir):
    os.mkdir(output_dir)


output_json_data = {}
chapter_pages: dict[int, set[int]] = {}
section_pages: dict[int, set[int]] = {}
catagory_pages: dict[str, set[int]] = {}
episode_page_name: dict[int, tuple[str, str, str]] = {}
used_image_set: set[str] = set()
page_name_count: dict[str, int] = {}
for json_file_name in sorted(os.listdir(dir_to_jsons)):
    episode_name = os.path.splitext(json_file_name)[0]
    output_file_name = os.path.join(output_dir, episode_name + ".txt")
    if episode_name.startswith("daily") or episode_name not in episode_table:
        print("not handled:", episode_name)
        continue
    chapter_id, section_id, episode_id, title, subtitle = episode_table[episode_name]
    # print(json_file_name, title, subtitle, chapter_table[chapter_id], section_table[section_id])
    catagory = get_file_catagory(json_file_name)
    chapter_name = chapter_table[chapter_id]
    section_name = section_table[section_id][1]
    section_pages.setdefault(section_id, set()).add(episode_id)
    chapter_pages.setdefault(chapter_id, set()).add(section_id)
    catagory_pages.setdefault(catagory + "剧情", set()).add(chapter_id)
    output_lines = []
    with open(output_file_name, "w") as fo:
        output_lines.append(
            "{{面包屑|"
            + catagory
            + "剧情|篇章："
            + chapter_name
            + "|章节："
            + section_name
            + "}}\n"
        )
        output_lines.append("{{#Widget:ScenarioStyles}}\n")
        output_lines.append("'''类型''': [[" + catagory + "剧情]]<br>\n")
        output_lines.append(
            "'''所属篇章''': [[篇章：" + chapter_name + "|" + chapter_name + "]]<br>\n"
        )
        output_lines.append(
            "'''所属章节''': [[章节：" + section_name + "|" + section_name + "]]<br>\n"
        )
        output_lines.append("'''当前剧目标题''': " + title + "<br>\n")
        output_lines.append("'''副标题''': " + subtitle + "<br>\n")
        output_lines.append('<div style="display:inline-block;width:100%;">\n')
        json_data = json.load(open(os.path.join(dir_to_jsons, json_file_name)))
        unit_names = {}
        env = {}
        for order in json_data["order_list"]:
            assert len(order.keys()) == 1
            order_name = list(order.keys())[0]
            if result_str := process_order(
                order_name,
                order[order_name],
                unit_names,
                env,
                used_image_set,
                bgm_table,
                costume_table,
            ):
                env["last_valid_order"] = order_name
                output_lines.append(result_str + "\n")
        output_lines.append("</div>\n")
        output_lines.append("[[分类:剧本]]")
        fo.write("".join(output_lines))
    cur_json_data = {"content": "".join(output_lines), "id": episode_id}
    page_name = catagory + "剧本：" + title
    if page_name not in page_name_count:
        page_name_count[page_name] = 1
    else:
        page_name_count[page_name] += 1
        print(
            "note: "
            + page_name
            + " already in the set, append "
            + str(page_name_count[page_name])
        )
        page_name += str(page_name_count[page_name])
    output_json_data[page_name] = cur_json_data
    episode_page_name[episode_id] = (title, subtitle, page_name)


# -------------------- hard coded episodes-------------------
unit_release_table: dict[int, int] = {}
with open(os.path.join(dir_to_data, "UnitReincarnationReleaseTable.csv")) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        unit_id = int(row["unit_id"])
        release_function = json.loads(row["release_function"].replace("|", ","))
        if "2" in release_function:
            costume_id = release_function["2"]
            unit_release_table[unit_id] = costume_id

unit_release_voice_table: dict[int, str] = {}
with open(os.path.join(dir_to_data, "VoiceTable.csv")) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        if row["voice_type_id"] == "7":
            unit_release_voice_table[int(row["unit_id"])] = row["voice_text"]

for unit_id, costume_id in unit_release_table.items():
    catagory = "衣装解放"
    chapter_id = -1
    section_id = -(10000000 - int(unit_id))
    episode_id = -(10000000 - int(str(unit_id) + "01") - 1)
    title = unit_table[unit_id] + "的服装解放演出"
    subtitle = ""
    page_name = catagory + "剧本：" + title
    assert (
        section_id in section_pages
        and chapter_id in chapter_pages
        and catagory + "剧情" in catagory_pages
    )
    section_pages[section_id].add(episode_id)
    chapter_name = chapter_table[chapter_id]
    section_name = section_table[section_id][1]
    content = (
        "{{面包屑|" + catagory + "剧情|篇章：" + chapter_name + "|章节：" + section_name + "}}\n"
    )
    content += "{{#Widget:ScenarioStyles}}\n"
    content += "'''类型''': [[" + catagory + "剧情]]<br>\n"
    content += "'''所属篇章''': [[篇章：" + chapter_name + "|" + chapter_name + "]]<br>\n"
    content += "'''所属章节''': [[章节：" + section_name + "|" + section_name + "]]<br>\n"
    content += "'''当前剧目标题''': " + title + "<br>\n"
    content += "'''副标题''': " + subtitle + "<br>\n"
    content += '<div style="display:inline-block;width:100%;">\n'
    content += "{{剧本模板事件|文本=播放BGM：" + bgm_table[1001] + "}}\n"
    unit_name, name = costume_table[int(costume_id)]
    content += (
        "{{剧本模板事件|图片=CH"
        + str(costume_id)
        + ".png|文本=介绍角色：\n"
        + unit_name
        + "\n【"
        + name
        + "】}}\n"
    )
    content += (
        "{{剧本模板对话框|图片=S"
        + str(costume_id)
        + ".png|角色名="
        + unit_name
        + "|文本="
        + wrap(unit_release_voice_table[unit_id])
        + "}}\n"
    )
    content += "{{剧本模板事件|文本=BGM停止}}\n"
    content += "</div>\n"
    content += "[[分类:剧本]]"
    cur_json_data = {"content": content, "id": episode_id}
    output_json_data[page_name] = cur_json_data
    episode_page_name[episode_id] = (title, subtitle, page_name)
    episode_id_table[episode_id] = page_name
    episode_table[page_name] = chapter_id, section_id, episode_id, title, subtitle

# -----------------------------------------------------------

for page_name, page_json_data in output_json_data.items():
    episode_id = page_json_data["id"]
    previous_episode_id = None
    next_episode_id = None
    episode_name = episode_id_table[episode_id]
    chapter_id, section_id, episode_id, title, subtitle = episode_table[episode_name]
    cur_section_episode_list = sorted(section_pages[section_id])
    episode_pos_in_section = cur_section_episode_list.index(episode_id)
    if episode_pos_in_section == 0:
        # first one in section, find previous section in chapter if exists
        cur_chapter_section_list = sorted(chapter_pages[chapter_id])
        section_pos_in_chapter = cur_chapter_section_list.index(section_id)
        if section_pos_in_chapter == 0:
            previous_episode_id = None
        else:
            previous_section_id = cur_chapter_section_list[section_pos_in_chapter - 1]
            previous_episode_id = sorted(section_pages[previous_section_id])[-1]
    else:
        previous_episode_id = cur_section_episode_list[episode_pos_in_section - 1]
    if episode_pos_in_section == len(cur_section_episode_list) - 1:
        # last one in section, find next section in the chapter if exist
        cur_chapter_section_list = sorted(chapter_pages[chapter_id])
        section_pos_in_chapter = cur_chapter_section_list.index(section_id)
        if section_pos_in_chapter == len(cur_chapter_section_list) - 1:
            next_episode_id = None
        else:
            next_section_id = cur_chapter_section_list[section_pos_in_chapter + 1]
            next_episode_id = sorted(section_pages[next_section_id])[0]
    else:
        next_episode_id = cur_section_episode_list[episode_pos_in_section + 1]
    if previous_episode_id:
        previous_title, previous_subtitle, previous_page_name = episode_page_name[
            previous_episode_id
        ]
        page_json_data["content"] += (
            "\n上一话：[["
            + previous_page_name
            + "|"
            + previous_title
            + subtitle_wrapper(previous_subtitle)
            + "]]\n"
        )
    else:
        page_json_data["content"] += "上一话：无，这是篇章第一话\n"
    page_json_data["content"] += "<br>"
    if next_episode_id:
        next_title, next_subtitle, next_page_name = episode_page_name[next_episode_id]
        page_json_data["content"] += (
            "\n下一话：[["
            + next_page_name
            + "|"
            + next_title
            + subtitle_wrapper(next_subtitle)
            + "]]\n"
        )
    else:
        page_json_data["content"] += "下一话：无，篇章结束\n"


with open(os.path.join("./local_files", "image_list.txt"), "w") as used_image_file:
    for image_path in sorted(used_image_set):
        used_image_file.write(image_path + "\n")

with open(
    os.path.join("./tracking_files", "comic_pages.json"),
    "w",
    encoding="utf-8",
) as comic_pages_json:
    for k in output_json_data.keys():
        assert "[" not in k and "]" not in k
    json.dump(output_json_data, comic_pages_json, ensure_ascii=False, indent=4)

catagory_data = {}
for catagory_name, chapter_list in catagory_pages.items():
    d = {}
    content = ""
    for chapter_id in sorted(chapter_list):
        content += "{{#lst:篇章：" + chapter_table[chapter_id] + "}}\n"
    d["content"] = content
    catagory_data[catagory_name] = d
with open(
    os.path.join("./tracking_files", "catagory_pages.json"), "w", encoding="utf-8"
) as json_file:
    for k in catagory_data.keys():
        assert "[" not in k and "]" not in k
    json.dump(catagory_data, json_file, ensure_ascii=False, indent=4)


chapter_data = {}
for chapter_id, section_list in chapter_pages.items():
    d = {}
    content = ""
    chapter_uniq_id = (chapter_id + 1000000) * 10
    fold_id1 = str(chapter_uniq_id + 1)
    fold_id2 = str(chapter_uniq_id + 2)
    content += "{{#Widget:ChapterSectionDisplay}}\n"
    if chapter_id == -1:
        content += "{{#Widget:UnitChapterStyles}}\n"
    content += "{{折叠面板|开始|主框=" + fold_id1 + "}}\n"
    content += (
        "{{折叠面板|标题="
        + chapter_table[chapter_id]
        + "|选项="
        + fold_id1
        + "|主框="
        + fold_id1
        + "|样式=warning|展开=是}}\n"
    )
    content += "{{板块|内容开始}}\n"
    if chapter_id in chapter_kanban_info:
        costume_id, unit_speech_group_id = chapter_kanban_info[chapter_id]
        content += "{{折叠面板|开始|主框=" + fold_id2 + "}}\n"
        content += (
            "{{折叠面板|标题=展开查看看板|选项=" + fold_id2 + "|主框=" + fold_id2 + "|样式=warning}}\n"
        )
        content += "{{章节看板|角色服装=" + str(costume_id)
        for idx, speech in enumerate(unit_speech_group_table[unit_speech_group_id]):
            content += "|对话" + str(idx + 1) + "=" + wrap(speech)
        content += "}}\n"
        content += "{{折叠面板|内容结束}}\n"
    if chapter_id == -1:
        content += '<div class="units-grid">\n'
        for section_id in sorted(section_list):
            cur_unit_id = 10000000 + section_id
            section_name = section_table[section_id][1]
            content += '<div class="unit-wrapper">\n'
            content += '<div class="unit-img-wrapper">\n'
            content += (
                "[[文件:S"
                + str(cur_unit_id)
                + "01.png|60px|link=章节："
                + section_name
                + "]]\n"
            )
            content += "</div>\n"
            content += '<div class="unit-name-wrapper">\n'
            content += (
                "[[章节：" + section_name + "|" + unit_short_name[cur_unit_id] + "]]\n"
            )
            content += "</div>\n"
            content += "</div>\n"
        content += "</div>\n"
    else:
        for section_id in sorted(section_list):
            section_name = section_table[section_id][1]
            section_subtitle = section_table[section_id][2]
            content += (
                "<div>{{板块|按钮|章节："
                + section_name
                + "|"
                + section_name
                + subtitle_wrapper(section_subtitle)
                + "}}</div>\n"
            )
    content += "{{板块|内容结束}}\n"
    content += "{{板块|结束}}\n"
    content += "{{折叠面板|内容结束}}\n"
    content += "-------------------------------\n"
    d["content"] = content
    chapter_data["篇章：" + chapter_table[chapter_id]] = d
with open(
    os.path.join("./tracking_files", "chapter_pages.json"), "w", encoding="utf-8"
) as json_file:
    for k in chapter_data.keys():
        assert "[" not in k and "]" not in k
    json.dump(chapter_data, json_file, ensure_ascii=False, indent=4)

section_data = {}
for section_id, episode_list in section_pages.items():
    d = {}
    chapter_name = chapter_table[section_table[section_id][0]]
    content = ""
    content += "{{面包屑|篇章：" + chapter_name + "}}\n"
    content += "{{#Widget:ChapterSectionDisplay}}\n"
    section_name = section_table[section_id][1] + subtitle_wrapper(
        section_table[section_id][2]
    )
    content += "{{折叠面板|开始|主框=1}}\n"
    content += "{{折叠面板|标题=" + section_name + "|选项=1|主框=1|样式=primary|展开=是}}\n"
    content += "{{板块|内容开始}}\n"
    if section_id in section_kanban_info:
        costume_id, unit_speech_group_id = section_kanban_info[section_id]
        content += "{{折叠面板|开始|主框=2}}\n"
        content += "{{折叠面板|标题=展开查看看板|选项=2|主框=2|样式=primary}}\n"
        content += "{{章节看板|角色服装=" + str(costume_id)
        for idx, speech in enumerate(unit_speech_group_table[unit_speech_group_id]):
            content += "|对话" + str(idx + 1) + "=" + wrap(speech)
        content += "}}\n"
        content += "{{折叠面板|内容结束}}\n"
    for episode_id in sorted(episode_list):
        title, subtitle, page_name = episode_page_name[episode_id]
        content += (
            "<div>{{板块|按钮|"
            + page_name
            + "|"
            + title
            + subtitle_wrapper(subtitle)
            + "}}</div>\n"
        )
    content += "{{板块|内容结束}}\n"
    content += "{{板块|结束}}\n"
    content += "{{折叠面板|内容结束}}\n"

    cur_chapter_section_list = sorted(chapter_pages[section_table[section_id][0]])
    section_pos_in_chapter = cur_chapter_section_list.index(section_id)
    if section_pos_in_chapter > 0:
        previous_section_id = cur_chapter_section_list[section_pos_in_chapter - 1]
        _, previous_section_title, previous_section_subtitle = section_table[
            previous_section_id
        ]
        content += (
            "上一章节：[[章节："
            + previous_section_title
            + "|"
            + previous_section_title
            + subtitle_wrapper(previous_section_subtitle)
            + "]]\n"
        )
    else:
        content += "上一章节：无，这是篇章第一节\n"
    content += "<br>"
    if section_pos_in_chapter < len(cur_chapter_section_list) - 1:
        next_section_id = cur_chapter_section_list[section_pos_in_chapter + 1]
        _, next_section_title, next_section_subtitle = section_table[next_section_id]
        content += (
            "下一章节：[[章节："
            + next_section_title
            + "|"
            + next_section_title
            + subtitle_wrapper(next_section_subtitle)
            + "]]\n"
        )
    else:
        content += "下一章节：无，篇章结束\n"
    content += "[[分类:章节]]"

    d["content"] = content
    section_data["章节：" + section_table[section_id][1]] = d

with open(
    os.path.join("./tracking_files", "section_pages.json"), "w", encoding="utf-8"
) as json_file:
    for k in section_data.keys():
        assert "[" not in k and "]" not in k
    json.dump(section_data, json_file, ensure_ascii=False, indent=4)
