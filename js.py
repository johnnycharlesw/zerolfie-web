import pythonmonkey as pm
import sys
import os
import threading
from contextlib import contextmanager
from typing import Any, Optional, Mapping
from queue import Queue
import subprocess
import json as _json

_thread_local = threading.local()


def _invoke_eval(js_source: str):
    """Evaluate JavaScript source using PythonMonkey and return the result."""
    return pm.eval(js_source)


class _Console(object):
    def log(self, *args):
        print(*args)

    def error(self, *args):
        print(*args, file=sys.stderr)

    def warn(self, *args):
        print(*args, file=sys.stderr)


def _use_ctx():
    """Deprecated: no JS context manager needed with PythonMonkey."""
    raise RuntimeError("Direct context usage is not supported; use run_code/define/call.")


def init(globals: Optional[Mapping[str, Any]] = None) -> None:
    """
    Initialize the JS runtime (idempotent). Optionally inject globals.
    Usage:
        import js
        js.init({"pyVersion": "3.x"})
    """
    if not globals:
        return
    import json
    assignments = []
    for key, value in globals.items():
        js_value = json.dumps(value)
        assignments.append(f"globalThis['{key}'] = {js_value}")
    if assignments:
        _invoke_eval(";".join(assignments))


def set_global(name: str, value: Any) -> None:
    """Set one top-level global value in the JS context."""
    import json
    # Handle Python callables by installing JS stubs to avoid serialization errors
    if callable(value):
        if name in ("setTimeout", "setInterval"):
            # Return a dummy timer id; timers are currently handled by the Python side
            _invoke_eval(
                f"globalThis['{name}'] = function(callback, delay){{ return 0; }}"
            )
            return
        if name in ("clearTimeout", "clearInterval"):
            _invoke_eval(
                f"globalThis['{name}'] = function(id){{ /* no-op */ }}"
            )
            return
        # Generic no-op stub for unsupported Python function bindings
        _invoke_eval(
            f"globalThis['{name}'] = function(){ { 'return undefined;' } }"
        )
        return
    _invoke_eval(f"globalThis['{name}'] = {json.dumps(value)}")


def run_code(source: str) -> Any:
    """
    Execute a JavaScript source string.
    Returns the value of the last evaluated expression (if any).
    """
    return _invoke_eval(source)


def run_code_isolated(source: str, timeout_ms: int = 3000) -> bool:
    """
    Execute JavaScript source in a separate Python subprocess using PythonMonkey.
    Returns True if execution completed without an unhandled error; False otherwise.
    This prevents native crashes from taking down the main process.
    """
    runner = (
        "import sys, json\n"
        "try:\n"
        "    import pythonmonkey as pm\n"
        "    code = sys.stdin.read()\n"
        "    pm.eval(code)\n"
        "    print(json.dumps({'ok': True}))\n"
        "except Exception as e:\n"
        "    print(json.dumps({'ok': False, 'error': str(e)}))\n"
    )
    try:
        proc = subprocess.run(
            [sys.executable, "-c", runner],
            input=source.encode("utf-8", errors="replace"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=max(0.1, timeout_ms / 1000.0),
        )
        try:
            out = proc.stdout.decode("utf-8", errors="replace").strip()
            data = _json.loads(out) if out else {"ok": False}
            return bool(data.get("ok"))
        except Exception:
            return False
    except subprocess.TimeoutExpired:
        return False


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
    js = f"globalThis['{name}'] = ({source_fn}); globalThis['{name}'];"
    return _invoke_eval(js)


def call(func_name: str, *args: Any) -> Any:
    """
    Call a function by name that exists in the global JS scope.
    """
    import json
    # Serialize arguments to JSON and invoke the function in JS
    json_args = ", ".join(json.dumps(a) for a in args)
    js = f"(function() {{ const fn = globalThis['{func_name}']; if (!fn) throw new Error('JS function \'{func_name}\' not found'); return fn({json_args}); }})()"
    return _invoke_eval(js)


# If run as an entry point, run an REPL

def repl():
    """Run a simple JS REPL on stdin."""
    print("JavaScript REPL (type 'exit' or Ctrl-D to quit)")
    while True:
        try:
            line = input("js> ")
            if line.strip().lower() in ("exit", "quit"):
                break
            if line.strip() == "":
                continue
            result = run_code(line)
            if result is not None:
                print(repr(result))
        except (EOFError, KeyboardInterrupt):
            print()
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    if sys.argv[1] == "repl":
        repl()
    elif sys.argv[1] == "demo":
        demo()
    elif sys.argv[1] == "file":
        run_file(sys.argv[2])
    elif sys.argv[1] == "code":
        run_code(sys.argv[2])
    elif sys.argv[1] == "define":
        define(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == "call":
        call(sys.argv[2], *sys.argv[3:])
    elif sys.argv[1] == "init":
        init(sys.argv[2])
    elif sys.argv[1] == "set_global":
        set_global(sys.argv[2], sys.argv[3])
    else:
        print("Invalid argument")
    
