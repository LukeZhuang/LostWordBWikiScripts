#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
"""

import csv
import json
import os
import re
import sys


dir_to_jsons = sys.argv[1]
dir_to_data = sys.argv[2]


def wrap(text: str) -> str:
    text = text.replace("\n", "<br>")
    text = text.replace("~", "～")
    if "\u001b" in text:
        text = text.replace("\u001bh", "(主角名)")
        if "\u001b" in text:
            text = re.sub(r"\u001b[0-9a-z]+", "", text)
        assert "\u001b" not in text
    return text


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
        item_file = order["m_name"]
        if item_file.lower().startswith("graphics/comic/item/"):
            used_image_set.add("5 " + item_file)
            item_file = "CITM_" + item_file[20:]
        elif item_file.lower().startswith("graphics/thumbnail/items/"):
            used_image_set.add("6 " + item_file)
            item_file = "TITM" + item_file[25:]
        elif item_file.lower().startswith("graphics/comic/bg/"):
            used_image_set.add("7 " + item_file)
            item_file = "CBG" + item_file[18:]
        elif item_file.lower().startswith(
            "graphics/thumbnail/events/thumbnail_eventitem_"
        ):
            used_image_set.add("8 " + item_file)
            item_file = "EVEITM_" + item_file[46:]
        elif item_file.lower().startswith("graphics/thumbnail/groupicons/"):
            used_image_set.add("9 " + item_file)
            item_file = "GITM" + item_file[30:]
        elif item_file.lower().startswith("graphics/thumbnail/objects/"):
            used_image_set.add("10 " + item_file)
            item_file = "OBJITM" + item_file[27:]
        else:
            raise Exception("unhandled item file path")
        return "{{剧本模板事件|图片=" + item_file + "|文本=【展示物品】}}"
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
with open(os.path.join(dir_to_data, "UnitTable.csv")) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        unit_table[int(row["id"])] = row["name"] + row["symbol_name"]

costume_table: dict[int, tuple[str, str]] = {}
with open(os.path.join(dir_to_data, "CostumeTable.csv")) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        costume_table[int(row["id"])] = (unit_table[int(row["unit_id"])], row["name"])
if 104102 not in costume_table:
    costume_table[104102] = ("森近霖之助", "海之家「香霖堂」")
if 307201 not in costume_table:
    costume_table[307201] = ("上白泽慧音", "吞食历史")
if 201801 not in costume_table:
    costume_table[201801] = ("八意永琳", "绯苍的贤帝")

chapter_table: dict[int, str] = {}
with open(os.path.join(dir_to_data, "ChapterTable.csv")) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        chapter_table[int(row["id"])] = row["title"]

section_table: dict[int, tuple[int, str, str]] = {}
with open(os.path.join(dir_to_data, "SectionTable.csv")) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        section_table[int(row["id"])] = (
            int(row["chapter_id"]),
            row["title"],
            row["sub_title"],
        )

episode_table: dict[str, tuple[int, int, int, str, str]] = {}
episode_id_table: dict[int, str] = {}
with open(os.path.join(dir_to_data, "EpisodeTable.csv")) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        comic_filepath = "-".join(row["comic_filepath"].lower().split("/"))
        comic_filepath = extract_comic_filepath(comic_filepath)
        if not comic_filepath.startswith("daily"):
            assert (
                comic_filepath not in episode_table
                or episode_table[comic_filepath][3] == row["title"]
                or episode_table[comic_filepath][4] == row["sub_title"]
            )
        episode_table[comic_filepath] = (
            int(row["chapter_id"]),
            int(row["section_id"]),
            int(row["id"]),
            row["title"],
            row["sub_title"],
        )
        episode_id_table[int(row["id"])] = comic_filepath

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
        title = unit_table[int(row["unit_id"])] + "的衣装解放"
        subtitle = ""
        section_table[section_id] = (chapter_id, title, subtitle)
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
        title = row["title"]
        subtitle = row["comic_title"]
        section_table[section_id] = (chapter_id, title, subtitle)
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

with open(os.path.join(dir_to_data, "RelicQuestTable.csv")) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        comic_filepath = "-".join(row["comic_filepath"].lower().split("/"))
        comic_filepath = extract_comic_filepath(comic_filepath)
        if not comic_filepath.startswith("daily"):
            assert comic_filepath not in episode_table
        chapter_id = -3
        section_id = -(30000000 - int(row["id"]))
        episode_id = -(30000000 - int(row["id"]))
        title = row["title"]
        subtitle = "相关角色: " + unit_table[int(row["id"][:-2])]
        section_table[section_id] = (chapter_id, title, subtitle)
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

output_dir = os.path.join("./tracking_files", "comic_output")
if not os.path.exists(output_dir):
    os.mkdir(output_dir)


output_json_datas = []
output_json_data = {}
chapter_pages: dict[int, set[int]] = {}
section_pages: dict[int, set[int]] = {}
catagory_pages: dict[str, set[int]] = {}
episode_page_name: dict[int, tuple[str, str, str]] = {}
used_image_set: set[str] = set()
cnt = 0
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
                output_lines.append(result_str + "\n")
        output_lines.append("</div>\n")
        output_lines.append("[[分类:剧本]]")
        fo.write("".join(output_lines))
    cur_json_data = {"content": "".join(output_lines)}
    page_name = catagory + "剧本：" + title
    assert page_name not in output_json_data
    output_json_data[page_name] = cur_json_data
    episode_page_name[episode_id] = (title, subtitle, page_name)
    cnt += 1
    if cnt % 500 == 0:
        output_json_datas.append(output_json_data)
        output_json_data = {}
output_json_datas.append(output_json_data)


with open(os.path.join("./local_files", "image_list.txt"), "w") as used_image_file:
    for image_path in sorted(used_image_set):
        used_image_file.write(image_path + "\n")

for idx, json_data in enumerate(output_json_datas):
    with open(
        os.path.join("./local_files", "comic_pages_part" + str(idx) + ".json"),
        "w",
        encoding="utf-8",
    ) as comic_pages_json:
        json.dump(json_data, comic_pages_json, ensure_ascii=False, indent=4)

catagory_data = {}
for catagory_name, chapter_list in catagory_pages.items():
    d = {}
    content = ""
    for chapter_id in sorted(chapter_list):
        content += "{{#lst:篇章：" + chapter_table[chapter_id] + "}}\n"
    d["content"] = content
    catagory_data[catagory_name] = d
with open(
    os.path.join("./local_files", "catagory_pages.json"), "w", encoding="utf-8"
) as json_file:
    json.dump(catagory_data, json_file, ensure_ascii=False, indent=4)


chapter_data = {}
for chapter_id, section_list in chapter_pages.items():
    d = {}
    content = ""
    content += "{{折叠面板|开始|主框=1}}\n"
    content += (
        "{{折叠面板|标题=" + chapter_table[chapter_id] + "|选项=1|主框=1|样式=warning|展开=是}}\n"
    )
    content += "{{板块|内容开始}}\n"
    for section_id in sorted(section_list):
        section_name = section_table[section_id][1]
        content += "{{板块|按钮|章节：" + section_name + "|" + section_name + "}}"
    content += "{{板块|内容结束}}\n"
    content += "{{板块|结束}}\n"
    content += "{{折叠面板|内容结束}}\n"
    d["content"] = content
    chapter_data["篇章：" + chapter_table[chapter_id]] = d
with open(
    os.path.join("./local_files", "chapter_pages.json"), "w", encoding="utf-8"
) as json_file:
    json.dump(chapter_data, json_file, ensure_ascii=False, indent=4)

section_data = {}
for section_id, episode_list in section_pages.items():
    d = {}
    content = ""
    chapter_name = chapter_table[section_table[section_id][0]]
    content += "{{面包屑|篇章：" + chapter_name + "}}"
    content += '<div style="overflow:auto">\n'
    content += (
        "<div class=\"section_title\">'''章节标题'''："
        + section_table[section_id][1]
        + "</div>\n"
    )
    content += (
        "<div class=\"section_subtitle\">'''章节副标题'''："
        + section_table[section_id][2]
        + "</div>\n"
    )
    content += (
        "<div class=\"section_belonging\">'''所属篇章'''：[[篇章："
        + chapter_name
        + "|"
        + chapter_name
        + "]]</div>\n"
    )
    content += "<br><br>"
    content += '<div class="episodes_wrapper">\n'
    for episode_id in sorted(episode_list):
        content += '<div class="episode_li">'
        title, subtitle, page_name = episode_page_name[episode_id]
        content += (
            '<div class="episode_title">[[' + page_name + "|" + title + "]]</div>"
        )
        content += '<div class="episode_subtitle">  - ' + subtitle + "</div>"
        content += "</div>\n"
        content += "<br>"
    content += "</div>\n"
    content += "</div>"
    d["content"] = content
    section_data["章节：" + section_table[section_id][1]] = d
with open(
    os.path.join("./local_files", "section_pages.json"), "w", encoding="utf-8"
) as json_file:
    json.dump(section_data, json_file, ensure_ascii=False, indent=4)
