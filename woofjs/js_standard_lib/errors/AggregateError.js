class AggregateErrorConstructor extends Error {
    name = "AggregateError";
    errors = [];

    __WoofJS_addError(error){
        this.errors.push(error);
    }
}
globalThis.AggregateError = AggregateErrorConstructor;