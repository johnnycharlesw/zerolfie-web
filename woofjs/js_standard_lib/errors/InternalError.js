// Define the class
class InternalErrorConstructor extends Error {
    name = "InternalError";
}
globalThis.InternalError=InternalErrorConstructor; // expose it for WoofJS to throw if needed