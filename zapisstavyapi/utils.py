from collections.abc import Callable
from functools import wraps
from typing import Any


def get_func_name(func: Callable[..., Any], args: tuple[Any, ...]) -> str:
    """Helper function for function name logging.

    Args:
        func: python function
        args: arguments to the function

    Returns: function name
    """
    # check if first argument is class instance (self)
    if args and hasattr(args[0], func.__name__):
        return f"{args[0].__class__.__name__}.{func.__name__}"

    return func.__name__


def log_func(
    func: Callable[..., Any], log_func: Callable[..., Any] = print
) -> Callable[..., Any]:
    """Decorator for logging functions.

    Args:
        func: func to be decorated
        log_func: function used for logging, e.g.: logger.debug, print, etc.

    Returns: decorator
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        func_name = get_func_name(func, args)

        log_func(f"{func_name} was called.")
        result = func(*args, **kwargs)
        log_func(f"{func_name} finished.")

        return result

    return wrapper
