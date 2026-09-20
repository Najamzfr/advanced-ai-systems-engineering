.PHONY: setup run evaluate grade test clean $(addprefix check-step-,1 2 3 4 5 6 7 8 9 10 11 12)
setup:
	python -m course.check setup
run:
	python project.py --allow-sample
evaluate:
	python project.py --require-real-data --course-work-root $${COURSE_WORK_ROOT:?set COURSE_WORK_ROOT to the folder containing Weeks 1-7}
grade:
	python -m course.check grade
test:
	python -m unittest discover -s tests -v
check-step-%:
	python -m course.check check-step-$*
clean:
	rm -rf reports data/release.jsonl
