.PHONY: setup run evaluate grade test stack-up telemetry $(addprefix check-step-,1 2 3 4 5 6 7 8 9 10 11 12)
setup:
	python -m course.check check-step-1 || true
run:
	python project.py --allow-sample --approve
evaluate:
	python project.py --require-real-data --approve
grade:
	python -m course.check grade
test:
	python -m unittest discover -s tests -v
stack-up:
	docker compose up -d
telemetry:
	python scripts/emit_telemetry.py
check-step-1:
	python -m course.check check-step-1
check-step-2:
	python -m course.check check-step-2
check-step-3:
	python -m course.check check-step-3
check-step-4:
	python -m course.check check-step-4
check-step-5:
	python -m course.check check-step-5
check-step-6:
	python -m course.check check-step-6
check-step-7:
	python -m course.check check-step-7
check-step-8:
	python -m course.check check-step-8
check-step-9:
	python -m course.check check-step-9
check-step-10:
	python -m course.check check-step-10
check-step-11:
	python -m course.check check-step-11
check-step-12:
	python -m course.check check-step-12
