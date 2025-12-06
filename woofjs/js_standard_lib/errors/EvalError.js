class EvalErrorConstructor extends Error {
    constructor(message = '') {
        super(message);
        this.name = "EvalError";
      }
}
globalThis.EvalError=EvalErrorConstructor;