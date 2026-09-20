PYTHON ?= python3
.PHONY: setup run evaluate grade test $(addprefix check-step-,$(shell seq 1 12))
setup:
	$(PYTHON) scripts/fetch_data.py --cases 25
run: setup
	$(PYTHON) project.py
evaluate: run
grade: evaluate
	$(PYTHON) course/check.py grade
test:
	$(PYTHON) -m unittest discover -s tests -v
check-step-%:
	$(PYTHON) course/check.py check-step-$*
