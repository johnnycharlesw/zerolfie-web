import STPyV8 as v8js
import sys
import os
import threading
from contextlib import contextmanager
from typing import Any, Optional, Mapping

# Internal single shared context + lock for serialized access
_jsctx = v8js.JSContext()
_lock = threading.RLock()
_initialized = False


class _Console(object):
    def log(self, *args):
        print(*args)

    def error(self, *args):
        print(*args, file=sys.stderr)

    def warn(self, *args):
        print(*args, file=sys.stderr)


@contextmanager
def _use_ctx():
    """Enter the shared JS context with serialization and one-time init."""
    global _initialized
    with _lock:
        _jsctx.enter()
        try:
            if not _initialized:
                # Provide a minimal console implementation in JS
                _jsctx.locals.console = _Console()
                _initialized = True
            yield _jsctx
        finally:
            _jsctx.leave()


def init(globals: Optional[Mapping[str, Any]] = None) -> None:
    """
    Initialize the JS runtime (idempotent). Optionally inject globals.
    Usage:
        import js
        js.init({"pyVersion": "3.x"})
    """
    with _use_ctx() as ctx:
        if globals:
            for k, v in globals.items():
                setattr(ctx.locals, k, v)


def set_global(name: str, value: Any) -> None:
    """Set one top-level global value in the JS context."""
    with _use_ctx() as ctx:
        setattr(ctx.locals, name, value)


def run_code(source: str) -> Any:
    """
    Execute a JavaScript source string in the shared context.
    Returns the value of the last evaluated expression (if any).
    """
    with _use_ctx() as ctx:
        return ctx.eval(source)


def run_file(path: str, encoding: str = "utf-8") -> Any:
    """
    Execute a JavaScript file by path.
    Returns the value of the last evaluated expression (if any).
    """
    if not os.path.isfile(path):
        raise FileNotFoundError(path)
    with open(path, "r", encoding=encoding) as f:
        source = f.read()
    return run_code(source)


def define(name: str, source_fn: str) -> Any:
    """
    Define a named function in the global scope from a JS function source.
    Example:
        define('upcase', '(s) => String(s).toUpperCase()')
    Returns the created function object.
    """
    js = f"this['{name}'] = ({source_fn}); this['{name}'];"
    with _use_ctx() as ctx:
        return ctx.eval(js)


def call(func_name: str, *args: Any) -> Any:
    """
    Call a function by name that exists in the global JS scope.
    """
    with _use_ctx() as ctx:
        fn = getattr(ctx.locals, func_name, None)
        if fn is None:
            # try via eval in case of non-identifier or nested names
            fn = ctx.eval(f"this['{func_name}']")
        if fn is None:
            raise AttributeError(f"JS function '{func_name}' not found")
        return fn(*args)


# Backward-compatible demo similar to earlier behavior
# Keeps the original HELLO WORLD! example working

def demo() -> None:
    """Demonstration: define and call a JS function."""
    define("upcase", "(s) => String(s).toUpperCase()")
    print(call("upcase", "hello world!"))


# If someone still calls init() expecting the previous sample to run,
# keep a small demonstration here as well. Comment out if undesired.

def _legacy_demo_if_needed():
    try:
        # demonstrate the context works, but do not fail hard if anything is off
        define("upcase", "(s) => String(s).toUpperCase()")
        print(call("upcase", "hello world!"))
    except Exception:
        pass


# Maintain previous side effect on init call for compatibility
# Remove the next two lines if you prefer init() to be side-effect free
# and only perform environment setup.
# init()  # ensure initialized
# _legacy_demo_if_needed()
