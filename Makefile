format:
	black -l 120 `git ls-files "*.py"`
checkstyle:
	black --check -l 120 `git ls-files "*.py"`
