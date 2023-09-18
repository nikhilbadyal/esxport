"""Common utilities."""
from __future__ import annotations

import time
from functools import wraps
from typing import Any, Callable, TypeVar

from loguru import logger

from src.constant import RETRY_DELAY, TIMES_TO_TRY
from src.exceptions import ESConnectionError

# Define type variable for exception class
T_Exception = TypeVar("T_Exception", bound=BaseException)


def retry(
    exception_to_check: type[T_Exception],
    tries: int = TIMES_TO_TRY,
    delay: int = RETRY_DELAY,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Retry connection."""

    def deco_retry(f: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(f)
        def f_retry(*args: Any, **kwargs: dict[str, Any]) -> Any:
            mtries = tries
            while mtries > 0:
                try:
                    return f(*args, **kwargs)
                except exception_to_check as e:  # noqa: PERF203
                    logger.error(e)
                    logger.info(f"Retrying in {delay} seconds ...")
                    time.sleep(delay)
                    mtries -= 1
            try:
                return f(*args, **kwargs)
            except exception_to_check as e:
                msg = f"Fatal Error: {e}"
                raise ESConnectionError(msg) from e

        return f_retry

    return deco_retry
