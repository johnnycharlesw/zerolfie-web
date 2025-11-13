class TypeErrorConstructor extends Error {
    name = "TypeError";
}
globalThis.TypeError=TypeErrorConstructor;