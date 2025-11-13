class ReferenceErrorConstructor extends Error {
    name = "ReferenceError";
}
globalThis.ReferenceError=ReferenceErrorConstructor;