import os
import re
import shutil
import sys
from PIL import Image

git_status_file = sys.argv[1]
source_dir = sys.argv[2]
output_dir = sys.argv[3]

watermark_image = Image.open(os.path.join(".", "watermark.png"))


def apply_watermark(original_image, watermark_image):
    wid, hgt = original_image.size
    wm_wid, wm_hgt = watermark_image.size
    left, right = (wid - wm_wid, hgt - wm_hgt)

    watermark = watermark_image.copy()
    # watermark.putalpha(128)

    sub_background = original_image.copy()
    sub_background = sub_background.crop((left, right, wid, hgt))
    composite = Image.alpha_composite(sub_background, watermark)

    output_image = original_image.copy()
    output_image.paste(composite, (left, right))
    return output_image


def parse_file(file_name, dest_dir, category, sub_category, prefix):
    if sub_category == "":
        regex_str = category + "/" + prefix + r"(.*)\.png"
    else:
        regex_str = category + "/" + sub_category + "/" + prefix + r"(.*)\.png"
    g = re.findall(regex_str, file_name)
    if len(g) == 0:
        return
    assert len(g) == 1

    source_file = os.path.join(source_dir, file_name)
    assert os.path.exists(source_file)
    new_dest_dir = os.path.join(dest_dir, category)
    if not os.path.exists(new_dest_dir):
        os.mkdir(new_dest_dir)
    if sub_category != "":
        new_dest_dir = os.path.join(new_dest_dir, sub_category)
    if not os.path.exists(new_dest_dir):
        os.mkdir(new_dest_dir)

    image_name = g[0]
    new_file_name = prefix + image_name + ".png"

    # apply wather mark for G/AltCostume
    if category == "UnitFullBody" and sub_category == "AltCostume":
        print("apply water mark for:", new_file_name)
        original_image = Image.open(source_file)
        output_image = apply_watermark(original_image, watermark_image)
        output_image.save(os.path.join(new_dest_dir, new_file_name))
        return

    # rename UnitShotIcon
    if category == "UnitShotIcon":
        assert sub_category == "Original" and (prefix == "SHB" or prefix == "SPB")
        if prefix == "SHB":
            assert image_name.endswith("01A") or image_name.endswith("01B")
            if image_name.endswith("01A"):
                new_file_name = image_name[:-3] + " shot a.png"
            else:
                new_file_name = image_name[:-3] + " shot b.png"
        else:
            assert (
                image_name.endswith("01A")
                or image_name.endswith("01B")
                or image_name.endswith("01C")
            )
            if image_name.endswith("01A"):
                new_file_name = image_name[:-3] + " spell a.png"
            elif image_name.endswith("01B"):
                new_file_name = image_name[:-3] + " spell b.png"
            else:
                new_file_name = image_name[:-3] + " spell c.png"

    shutil.copy(source_file, os.path.join(new_dest_dir, new_file_name))


for line in open(git_status_file):
    l = line.strip()
    if "modified:" in line:
        l = l.replace("modified:", "").strip()
    parse_file(l, output_dir, "UnitChange", "AltCostume", "CH")
    parse_file(l, output_dir, "UnitChange", "Original", "CH")
    parse_file(l, output_dir, "UnitFullBody", "AltCostume", "G")
    parse_file(l, output_dir, "UnitFullBody", "Original", "G")
    parse_file(l, output_dir, "UnitShotIcon", "Original", "SHB")
    parse_file(l, output_dir, "UnitShotIcon", "Original", "SPB")
    parse_file(l, output_dir, "UnitSquare", "AltCostume", "S")
    parse_file(l, output_dir, "UnitSquare", "Original", "S")
    parse_file(l, output_dir, "ComicBackGround", "", "CBG")
