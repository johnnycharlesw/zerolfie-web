"""
WoofJS - A JavaScript engine written in Rust, embeddable in Python.

Usage:
    from zerolfie_web.js.woofjs import WoofJsRuntime
    
    runtime = WoofJsRuntime()
    result = runtime.eval("1 + 2 * 3")
    print(result)  # 7
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any

# Try to import the compiled Rust module
try:
    # When installed as a package, woofjs will be in site-packages
    import woofjs
except ImportError:
    # Development mode: try to load from the woofjs directory
    woofjs_path = Path(__file__).parent.parent.parent.parent / "woofjs"
    if woofjs_path.exists():
        sys.path.insert(0, str(woofjs_path.parent))
        try:
            import woofjs
        except ImportError:
            raise ImportError(
                "WoofJS Rust module not found. Please build it with: "
                "cd woofjs && maturin develop"
            )

from woofjs import WoofJsApi, WoofJsIoStream


class WoofJsRuntime:
    """
    Main runtime for executing JavaScript code with WoofJS.
    
    This class manages the JavaScript execution environment, including
    loading the standard library and providing access to the host API.
    """
    
    def __init__(self, load_stdlib: bool = True):
        """
        Initialize a new WoofJS runtime.
        
        Args:
            load_stdlib: If True, automatically load the JS standard library
        """
        self.host_api = WoofJsApi()
        self.stdout = WoofJsIoStream()
        self.stderr = WoofJsIoStream()
        self._stdlib_loaded = False
        
        if load_stdlib:
            self.load_stdlib()
    
    def load_stdlib(self) -> None:
        """Load the JavaScript standard library files."""
        if self._stdlib_loaded:
            return
        
        stdlib_dir = Path(__file__).parent.parent.parent.parent / "woofjs" / "js_standard_lib"
        
        if not stdlib_dir.exists():
            raise FileNotFoundError(f"Standard library directory not found: {stdlib_dir}")
        
        # Load order matters - dependencies first
        load_order = [
            # Core globals and host API
            "globals.js",
            "woofjs_internal.js",
            
            # Errors (Error must come first)
            "errors/Error.js",
            "errors/EvalError.js",
            "errors/RangeError.js",
            "errors/ReferenceError.js",
            "errors/SyntaxError.js",
            "errors/TypeError.js",
            "errors/URIError.js",
            "errors/AggregateError.js",
            "errors/SuppressedError.js",
            "errors/InternalError.js",
            
            # Fundamental types
            "fundamental/Object.js",
            "fundamental/Function.js",
            "fundamental/Boolean.js",
            "fundamental/Symbol.js",
            
            # Control abstractions
            "control_abstraction_objects/Iterator.js",
            "control_abstraction_objects/AsyncIterator.js",
            "control_abstraction_objects/Generator.js",
            "control_abstraction_objects/GeneratorFunction.js",
            "control_abstraction_objects/Promise.js",
            
            # Numbers and dates
            "numbers_and_dates/Number.js",
            "numbers_and_dates/Math.js",
            "numbers_and_dates/Date.js",
            
            # Global functions
            "global_functions/eval.js",
            "global_functions/parseFloat.js",
            "global_functions/parseInt.js",
            "global_functions/isNaN.js",
            "global_functions/isFinite.js",
            
            # I/O
            "input_and_output/Console.js",
            
            # Structured data
            "structured_data/JSON.js",
        ]
        
        # Inject __WoofJS__ host API before loading stdlib
        self._inject_host_api()
        
        # Load files in order
        for rel_path in load_order:
            file_path = stdlib_dir / rel_path
            if file_path.exists():
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        source = f.read()
                    self.eval(source)
                except Exception as e:
                    print(f"Warning: Failed to load {rel_path}: {e}", file=sys.stderr)
        
        self._stdlib_loaded = True
    
    def _inject_host_api(self) -> None:
        """Inject the __WoofJS__ host API object into the JS environment."""
        # This would need to be implemented based on how you expose Rust objects to JS
        # For now, this is a placeholder that shows the structure
        host_api_js = f"""
        const __WoofJS__ = {{
            NotANumber: NaN,
            Infinity: Infinity,
            primitiveValues: {{ undefined: undefined }},
            add: (a, b) => a + b,
            subtract: (a, b) => a - b,
            multiply: (a, b) => a * b,
            divide: (a, b) => a / b,
            remainder: (a, b) => a % b,
            getCurrentUnixTimestamp: (y2k38safe=true, inMilliseconds=true) => {{
                return Date.now();
            }},
            getRandomFraction: () => Math.random(),
            stdin: {{ 
                readLine: () => prompt("Input: ") || "",
                read: (size) => prompt("Input: ") || ""
            }},
            stdout: {{ append: (s) => console.log(s) }},
            stderr: {{ append: (s) => console.error(s) }},
        }};
        """
        self.eval(host_api_js)
    
    def eval(self, source: str) -> Any:
        """
        Evaluate JavaScript source code.
        
        Args:
            source: JavaScript source code string
            
        Returns:
            The result of evaluating the code
        """
        # For now, this is a placeholder
        # Once WoofJS can execute full JS (not just expressions), implement here
        # For now, fall back to PythonMonkey or return a placeholder
        try:
            # Try using the Rust expression evaluator
            if hasattr(woofjs, 'eval_expr'):
                return woofjs.eval_expr(source)
        except Exception:
            pass
        
        # Fallback: would need full JS execution engine
        raise NotImplementedError(
            "Full JavaScript execution not yet implemented. "
            "WoofJS currently only supports arithmetic expressions."
        )
    
    def run_file(self, file_path: str) -> Any:
        """
        Load and execute a JavaScript file.
        
        Args:
            file_path: Path to the JavaScript file
            
        Returns:
            The result of executing the file
        """
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
        return self.eval(source)


# Convenience exports
__all__ = ["WoofJsRuntime", "WoofJsApi", "WoofJsIoStream"]

