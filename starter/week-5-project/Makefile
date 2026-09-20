.PHONY: setup run evaluate grade test fetch $(addprefix check-step-,1 2 3 4 5 6 7 8 9 10 11 12)
setup:
	python -m course.check setup
run:
	python project.py --allow-sample
fetch:
	python scripts/fetch_data.py --cases 50
evaluate:
	python project.py --require-real-data
grade:
	python -m course.check grade
test:
	python -m unittest discover -s tests -v
check-step-%:
	python -m course.check check-step-$*
