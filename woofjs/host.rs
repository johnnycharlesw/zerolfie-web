use std::time::{SystemTime, UNIX_EPOCH};

use pyo3::prelude::*;

/// IO stream that reads/writes directly to Python's stdin/stdout/stderr.
#[pyclass]
pub struct WoofJsIoStream {
    stream: PyObject,
    stream_type: StreamType,
}

#[derive(Clone, Copy)]
enum StreamType {
    Stdin,
    Stdout,
    Stderr,
}

#[pymethods]
impl WoofJsIoStream {
    /// Create a new stream bound to Python's stdin, stdout, or stderr.
    /// 
    /// Args:
    ///     py: Python interpreter instance
    ///     stream_type: "stdin", "stdout", or "stderr" (default: "stdout")
    #[new]
    #[args(stream_type = "\"stdout\"")]
    fn new(py: Python<'_>, stream_type: &str) -> PyResult<Self> {
        let sys = py.import("sys")?;
        let (stream, stype) = match stream_type {
            "stdin" => (sys.getattr("stdin")?, StreamType::Stdin),
            "stderr" => (sys.getattr("stderr")?, StreamType::Stderr),
            _ => (sys.getattr("stdout")?, StreamType::Stdout), // default to stdout
        };
        
        Ok(WoofJsIoStream {
            stream: stream.to_object(py),
            stream_type: stype,
        })
    }

    /// Append text to the stream (writes immediately to stdout/stderr).
    /// For stdin, this is a no-op.
    pub fn append(&self, py: Python<'_>, s: &str) -> PyResult<()> {
        match self.stream_type {
            StreamType::Stdin => {
                // stdin doesn't support write, so this is a no-op
                Ok(())
            }
            StreamType::Stdout | StreamType::Stderr => {
                self.stream.call_method1(py, "write", (s,))?;
                // Flush to ensure immediate output
                self.stream.call_method0(py, "flush")?;
                Ok(())
            }
        }
    }

    /// Set the entire stream content (clears and writes).
    /// Note: For real stdout/stderr, this just writes the text.
    /// For stdin, this is a no-op.
    pub fn setText(&self, py: Python<'_>, s: &str) -> PyResult<()> {
        match self.stream_type {
            StreamType::Stdin => Ok(()), // Can't set stdin content
            StreamType::Stdout | StreamType::Stderr => {
                // For real streams, we can't "set" text, so we just write it
                self.append(py, s)
            }
        }
    }

    /// Read a line from stdin (or empty string for stdout/stderr).
    pub fn readLine(&self, py: Python<'_>) -> PyResult<String> {
        match self.stream_type {
            StreamType::Stdin => {
                // Call readline() on stdin
                let result = self.stream.call_method0(py, "readline")?;
                let line: String = result.extract(py)?;
                Ok(line)
            }
            StreamType::Stdout | StreamType::Stderr => {
                // Output streams don't support readline
                Ok(String::new())
            }
        }
    }

    /// Read all available input from stdin (or empty string for stdout/stderr).
    pub fn read(&self, py: Python<'_>, size: Option<usize>) -> PyResult<String> {
        match self.stream_type {
            StreamType::Stdin => {
                if let Some(n) = size {
                    // Read n characters
                    let result = self.stream.call_method1(py, "read", (n,))?;
                    let text: String = result.extract(py)?;
                    Ok(text)
                } else {
                    // Read until EOF
                    let result = self.stream.call_method0(py, "read")?;
                    let text: String = result.extract(py)?;
                    Ok(text)
                }
            }
            StreamType::Stdout | StreamType::Stderr => {
                // Output streams don't support read
                Ok(String::new())
            }
        }
    }

    /// Get the stream name (for debugging).
    pub fn getText(&self) -> String {
        match self.stream_type {
            StreamType::Stdin => "<stdin>".to_string(),
            StreamType::Stdout => "<stdout>".to_string(),
            StreamType::Stderr => "<stderr>".to_string(),
        }
    }
}

/// Host API exposed to the JS stdlib as `__WoofJS__`.
#[pyclass]
pub struct WoofJsApi {
    #[pyo3(get)]
    pub stdin: Py<WoofJsIoStream>,
    #[pyo3(get)]
    pub stdout: Py<WoofJsIoStream>,
    #[pyo3(get)]
    pub stderr: Py<WoofJsIoStream>,
}

#[pymethods]
impl WoofJsApi {
    #[new]
    fn new(py: Python<'_>) -> PyResult<Self> {
        let stdin = Py::new(py, WoofJsIoStream::new(py, "stdin")?)?;
        let stdout = Py::new(py, WoofJsIoStream::new(py, "stdout")?)?;
        let stderr = Py::new(py, WoofJsIoStream::new(py, "stderr")?)?;
        Ok(WoofJsApi { stdin, stdout, stderr })
    }

    // --- Numeric primitives used by globals.js ---

    #[classattr]
    pub const NotANumber: f64 = f64::NAN;

    #[classattr]
    pub const Infinity: f64 = f64::INFINITY;

    // Primitive values container; JS side only needs `undefined`.
    #[getter]
    pub fn primitiveValues(&self, py: Python<'_>) -> PyResult<PyObject> {
        let dict = PyDict::new(py);
        dict.set_item("undefined", py.None())?;
        Ok(dict.into())
    }

    // --- Arithmetic helpers (used by operatorHandlers / Math) ---

    pub fn add(&self, a: f64, b: f64) -> f64 {
        a + b
    }

    pub fn subtract(&self, a: f64, b: f64) -> f64 {
        a - b
    }

    pub fn mutiply(&self, a: f64, b: f64) -> f64 {
        a * b
    }

    pub fn divide(&self, a: f64, b: f64) -> f64 {
        a / b
    }

    // --- Time / randomness helpers ---

    #[args(y2k38safe = true, inMilliseconds = true)]
    pub fn getCurrentUnixTimestamp(
        &self,
        y2k38safe: bool,
        inMilliseconds: bool,
    ) -> i64 {
        // Ignore y2k38safe for now; use native 64-bit timestamp.
        let now = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap_or_default();
        if inMilliseconds {
            now.as_millis() as i64
        } else {
            now.as_secs() as i64
        }
    }

    pub fn getRandomFraction(&self) -> f64 {
        rand::random::<f64>()
    }

    // --- Object helpers ---

    pub fn preventExtensions(&self, _obj: &PyAny) {
        // Placeholder: real implementation would mark object as non-extensible.
    }

    // --- Microtask / scheduling ---

    pub fn queueMicrotask(&self, py: Python<'_>, callback: PyObject) -> PyResult<()> {
        // Very simple approximation: schedule via `call_soon` if asyncio loop exists,
        // otherwise fall back to immediate call.
        if let Ok(asyncio) = py.import("asyncio") {
            if let Ok(loop_obj) = asyncio.call_method0("get_event_loop") {
                let _ = loop_obj.call_method1("call_soon", (callback,));
                return Ok(());
            }
        }
        callback.call0(py).map(|_| ())
    }
}


