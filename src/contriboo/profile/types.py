from typing import Literal, TypeAlias


DaysRange: TypeAlias = int | Literal["all"]
"""Allowed period argument: positive day count or `"all"` for full history."""
