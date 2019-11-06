format:
	black -l 120 `git ls-files "*.py"`
check:
	black --check -l 120 `git ls-files "*.py"`
