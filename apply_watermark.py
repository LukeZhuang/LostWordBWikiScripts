#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
"""

from PIL import Image
import os
import sys

input_dir = sys.argv[1]
output_dir = sys.argv[2]


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


watermark_image = Image.open(os.path.join(".", "watermark.png"))
for image_file_name in sorted(os.listdir(input_dir)):
    output_path = os.path.join(output_dir, image_file_name)
    if os.path.exists(output_path):
        continue
    original_image = Image.open(os.path.join(input_dir, image_file_name))
    output_image = apply_watermark(original_image, watermark_image)
    output_image.save(output_path)
    print("finished:", image_file_name)
