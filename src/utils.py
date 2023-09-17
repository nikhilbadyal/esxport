"""Common utilities."""
import time
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

from loguru import logger

from src.constant import RETRY_DELAY, TIMES_TO_TRY
from src.exceptions import ESConnectionError

F = TypeVar("F", bound=Callable[..., Any])


def retry(
    exception_to_check: type[BaseException],
    tries: int = TIMES_TO_TRY,
    delay: int = RETRY_DELAY,
) -> Callable[[F], F]:
    """Retryn connection."""

    def deco_retry(f: Any) -> Any:
        @wraps(f)
        def f_retry(*args: Any, **kwargs: dict[Any, Any]) -> Any:
            mtries = tries
            while mtries > 0:
                try:
                    return f(*args, **kwargs)
                except exception_to_check as e:
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
