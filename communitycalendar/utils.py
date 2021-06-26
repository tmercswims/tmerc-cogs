from typing import Any, Callable, Iterable


def find_index(check: Callable[[Any], bool], arr: Iterable[Any]) -> int:
    for idx, ele in enumerate(arr):
        if check(ele):
            return idx
    raise ValueError("No element matching the provided check found.")
