import os
import sys
import shutil

src_img_path = sys.argv[1]
dst_img_path = sys.argv[2]

f = open("./local_files/shot_icon_list.txt")
for line in f:
    unit_id = str(int(line.strip()))
    file_list = ["SHB" + unit_id + "01A.png",
                 "SHB" + unit_id + "01B.png",
                 "SPB" + unit_id + "01A.png",
                 "SPB" + unit_id + "01B.png",
                 "SPB" + unit_id + "01C.png"]
    output_file_list = [unit_id + " shot a.png",
                        unit_id + " shot b.png",
                        unit_id + " spell a.png",
                        unit_id + " spell b.png",
                        unit_id + " spell c.png"]
    for i, img_file in enumerate(file_list):
        img_file_path = os.path.join(src_img_path, img_file)
        if os.path.exists(img_file_path):
            shutil.copy(img_file_path, os.path.join(dst_img_path, output_file_list[i]))
        else:
            print(img_file + " not found!")

