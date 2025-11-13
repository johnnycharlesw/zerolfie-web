class SyntaxErrorConstructor extends Error {
    name = "SyntaxError";
}
globalThis.SyntaxError = SyntaxErrorConstructor;