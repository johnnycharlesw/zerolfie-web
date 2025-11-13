class InternalErrorConstructor extends Error {
    name = "InternalError";
}
globalThis.InternalError=InternalErrorConstructor;