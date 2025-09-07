import json
import os
import sys

source_json = sys.argv[1]
split_count = int(sys.argv[2])

with open(source_json, 'r', encoding='utf-8') as f:
    json_data = json.load(f)

file_name = os.path.basename(source_json)
assert file_name.endswith(".json")
file_name = file_name[:-5]

def write_to_file(content, index):
    with open(os.path.join('local_files', file_name + '.part' + str(index) + '.json'), 'w', encoding='utf-8') as f:
        json_string = json.dumps(content, ensure_ascii=False, separators=(',\n', ': '))
        f.write(json_string)


files = os.listdir("./local_files")
for f in files:
    if f.startswith(file_name + ".part"):
        fpath = os.path.join("./local_files/", f)
        print("remove:", fpath)
        os.remove(os.path.join("./local_files", f))
part = {}
count = 0
part_id = 1
for key in json_data:
    count += 1
    part[key] = json_data[key]
    if count % split_count == 0:
        write_to_file(part, part_id)
        part = {}
        part_id += 1

if len(part) > 0:
    write_to_file(part, part_id)
