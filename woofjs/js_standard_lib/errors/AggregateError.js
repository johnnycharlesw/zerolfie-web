class AggregateErrorConstructor extends Error {
    name = "AggregateError";
    errors = [];

    __WoofJS_addError(error){
        this.errors.concat(error);
    }
}
globalThis.AggregateError = AggregateErrorConstructor;