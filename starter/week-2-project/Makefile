.PHONY: setup fetch run evaluate grade test $(foreach n,$(shell seq 1 12),check-step-$(n))
setup:
	python -m course.check setup
fetch:
	python scripts/fetch_data.py --cases 200
run:
	python project.py --allow-sample
evaluate:
	python project.py --require-real-data
grade:
	python -m course.check grade
test:
	python -m unittest discover -s tests -v
$(foreach n,$(shell seq 1 12),check-step-$(n)):
	python -m course.check $@
