import json
import os

with open(os.path.join("tracking_files", 'characters_wikidata.json'), 'r', encoding='utf-8') as f:
    json_data = json.load(f)

text = '{{角色数据\n'

data = json_data["博丽灵梦L1"]

for key in data:
    text += '|' + key + '=__' + key + '__' + '\n'

text += '}}'

with open('unit_wiki_template.txt', 'w', encoding='utf-8') as f:
    f.write(text)
