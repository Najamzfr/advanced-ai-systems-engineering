PYTHON ?= python3

.PHONY: setup run evaluate run-lora run-qlora install-lora test grade grade-lora
setup:
	$(PYTHON) scripts/fetch_data.py

run: setup
	$(PYTHON) project.py --limit 20

evaluate: setup
	$(PYTHON) project.py

install-lora:
	$(PYTHON) -m pip install -r requirements-lora.txt

run-lora: setup
	$(PYTHON) project.py --adapter-mode peft

run-qlora: setup
	$(PYTHON) project.py --adapter-mode peft --qlora

test:
	$(PYTHON) -m unittest discover -s tests -v

grade:
	$(PYTHON) -m course.check grade

grade-lora: grade

check-step-%:
	$(PYTHON) -m course.check step $*
