from collections.abc import Callable
from functools import wraps
from typing import Any, Iterable

from psycopg import sql


def format_sql_query(sql_query: sql.Composed) -> str:
    """Format SQL for logs."""
    sql_query_str = sql.as_string(sql_query)
    sql_query_lines = sql_query_str.split("\n")
    return " ".join([query_line.strip() for query_line in sql_query_lines])


def build_set_clause(columns: Iterable[str]) -> sql.Composed:
    """Build comma delimited SET clause: col = %(col)s from columns for UPDATE query.

    Args:
        columns: columns: iterable of column names

    Returns: SET clause as SQL query object
    """
    return sql.SQL(", ").join(
        sql.SQL("{columns} = {value_placeholder}").format(
            columns=sql.Identifier(col),
            value_placeholder=sql.Placeholder(col),
        )
        for col in columns
    )


def _get_func_name(func: Callable[..., Any], args: tuple[Any, ...]) -> str:
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


def log_async_func(log_func: Callable[..., Any] = print) -> Callable[..., Any]:
    """Decorator factory that accepts a logging function."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        """Decorator, that wraps the function."""

        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            func_name = _get_func_name(func, args)

            log_func(f"{func_name}() was called.")
            result = await func(*args, **kwargs)
            log_func(f"{func_name}() finished.")

            return result

        return async_wrapper

    return decorator


def log_func(log_func: Callable[..., Any] = print) -> Callable[..., Any]:
    """Decorator factory that accepts a logging function."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        """Decorator, that wraps the function."""

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            func_name = _get_func_name(func, args)

            log_func(f"{func_name}() was called.")
            result = func(*args, **kwargs)
            log_func(f"{func_name}() finished")

            return result

        return wrapper

    return decorator
