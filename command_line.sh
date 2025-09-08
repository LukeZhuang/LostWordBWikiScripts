rm -rf output && mkdir output
python3 collect_images_from_resource.py ../LostWordResources/asset_bundles_ch/aaa ../LostWordResources/asset_bundles_ch output
python3 generate_timeline_tables.py ../LostWordResourceExtractor/output/asset_bundles_ch/Timeline
python3 generate_unit_data.py ../LostWordDataDecrypterPy/outputs
python3 generate_picture_data.py ../LostWordDataDecrypterPy/outputs/PictureTable.json
python3 generate_comic_files.py ../LostWordResourceExtractor/output/asset_bundles_ch/Comic ../LostWordDataDecrypterPy/outputs
