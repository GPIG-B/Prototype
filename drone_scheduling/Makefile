SRC_FILES:=*.py drone_scheduling/
.PHONY: all check lint clean


all: check lint

check: $(SRC_FILES)
	mypy --strict $(SRC_FILES)

lint: $(SRC_FILES)
	flake8 $(SRC_FILES)

clean:
	rm -rf *.egg-info
