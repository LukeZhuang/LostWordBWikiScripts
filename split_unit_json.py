import json
import os

with open(os.path.join('tracking_files', 'characters_wikidata.json'), 'r', encoding='utf-8') as f:
    json_data = json.load(f)


def write_to_file(content, index):
    with open(os.path.join('local_files', 'characters_wikidata.part' + str(index) + '.json'), 'w', encoding='utf-8') as f:
        json_string = json.dumps(content, ensure_ascii=False, separators=(',\n', ': '))
        f.write(json_string)


part = {}
count = 0
part_id = 1
for key in json_data:
    count += 1
    part[key] = json_data[key]
    if count % 50 == 0:
        write_to_file(part, part_id)
        part = {}
        part_id += 1

if len(part) > 0:
    write_to_file(part, part_id)
