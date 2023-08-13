.PHONY: *

CFG:=sandbox.yml

install:
	python3.10 -m venv venv
	venv/bin/pip install -U pip
	venv/bin/pip install -r requirements.txt

run_collection:
	venv/bin/python src/collection.py --cfg ${CFG} > collection.log 2>&1

run_bbox_labeling:
	venv/bin/python src/bbox_labeling.py --cfg ${CFG} > bbox_labeling.log 2>&1

run_ocr_labeling:
	venv/bin/python src/ocr_labeling.py --cfg ${CFG} > ocr_labeling.log 2>&1
