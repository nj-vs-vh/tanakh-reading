from typing import Any

import pytest

from backend.utils import deduplicate_keeping_order


@pytest.mark.parametrize(
    "original, expected_deduplicated",
    [
        ([1, 2, 3, 4, 1], [1, 2, 3, 4]),
        ([1, 2, 2, 3, 4, 1, 1, 1, 5, 3], [1, 2, 3, 4, 5]),
        ([], []),
        ([1, 1, 1, 1, 1, 1, 1], [1]),
        ([1, "hello", 1, 1, 1, 1, 1], [1, "hello"]),
    ],
)
def test_deduplicate_keeping_order(original: list[Any], expected_deduplicated: list[Any]):
    assert deduplicate_keeping_order(original) == expected_deduplicated
