format:
	python -m black --line-length 120 --target-version py38 .
checkstyle:
	python -m black --line-length 120 --target-version py38 --check .
