class NavigateBack(Exception):
    """Raised when the user requests to go back to a previous menu."""


class ExitApplication(Exception):
    """Raised when the user requests to exit the application."""


_BACK_TOKENS = {":back", ":b", "/back"}
_EXIT_TOKENS = {":exit", ":quit", ":q", "/exit"}


def _get_builtin_input():
    b = __builtins__
    if isinstance(b, dict):
        return b["input"]
    return b.input


def _set_builtin_input(func):
    b = __builtins__
    if isinstance(b, dict):
        b["input"] = func
    else:
        b.input = func


_original_input = _get_builtin_input()


def _navigation_input(prompt=""):
    value = _original_input(prompt)
    command = value.strip().lower()

    if command in _BACK_TOKENS:
        raise NavigateBack()

    if command in _EXIT_TOKENS:
        raise ExitApplication()

    return value


def install_global_navigation_input():
    """Patch built-in input so navigation commands work across modules."""
    global _original_input

    current_input = _get_builtin_input()
    if current_input is _navigation_input:
        return

    _original_input = current_input
    _set_builtin_input(_navigation_input)