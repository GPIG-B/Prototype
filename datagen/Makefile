SRC_FILES:=*.py datagen/
.PHONY: all check lint


all: check lint

check: $(SRC_FILES)
	mypy --strict $(SRC_FILES)

lint: $(SRC_FILES)
	flake8 $(SRC_FILES)
