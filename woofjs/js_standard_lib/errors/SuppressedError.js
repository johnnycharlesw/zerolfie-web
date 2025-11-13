class SuppressedErrorConstructor extends Error {
    name = "SuppressedError";
    error = null;
    suppressed = null;
}
globalThis.SuppressedError=SuppressedErrorConstructor;