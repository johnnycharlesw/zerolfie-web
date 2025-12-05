// Minimal Promise implementation for WoofJS.
// Goal: spec-ish behavior for typical usage (then/catch/finally, resolve/reject, basic chaining),
// without relying on a browser environment.

// Simple microtask queue: try host hook, then queueMicrotask, then setTimeout 0.
const __woofJS_queueMicrotask =
  (typeof __WoofJS__ !== "undefined" && __WoofJS__.queueMicrotask)
    ? (fn) => __WoofJS__.queueMicrotask(fn)
    : (typeof queueMicrotask === "function")
      ? queueMicrotask
      : (fn) => setTimeout(fn, 0);

const PENDING = 0;
const FULFILLED = 1;
const REJECTED = 2;

class Promise {
  constructor(executor) {
    if (typeof executor !== "function") {
      throw new TypeError("Promise executor must be a function");
    }

    this._state = PENDING;
    this._value = undefined;
    this._handlers = []; // { onFulfilled, onRejected, resolve, reject }

    const resolve = (value) => {
      this._settle(FULFILLED, value);
    };

    const reject = (reason) => {
      this._settle(REJECTED, reason);
    };

    try {
      executor(resolve, reject);
    } catch (e) {
      reject(e);
    }
  }

  _settle(state, value) {
    if (this._state !== PENDING) {
      return;
    }
    if (state === FULFILLED && value === this) {
      return this._settle(REJECTED, new TypeError("Cannot fulfill promise with itself"));
    }

    // Thenable assimilation (very small subset of the spec)
    if (state === FULFILLED && value && (typeof value === "object" || typeof value === "function")) {
      let then;
      try {
        then = value.then;
      } catch (e) {
        return this._settle(REJECTED, e);
      }
      if (typeof then === "function") {
        let called = false;
        try {
          then.call(
            value,
            (v) => {
              if (!called) {
                called = true;
                this._settle(FULFILLED, v);
              }
            },
            (r) => {
              if (!called) {
                called = true;
                this._settle(REJECTED, r);
              }
            }
          );
        } catch (e) {
          if (!called) {
            this._settle(REJECTED, e);
          }
        }
        return;
      }
    }

    this._state = state;
    this._value = value;
    this._flushHandlers();
  }

  _flushHandlers() {
    if (this._state === PENDING) return;
    const handlers = this._handlers;
    this._handlers = [];

    __woofJS_queueMicrotask(() => {
      for (const h of handlers) {
        this._handle(h);
      }
    });
  }

  _handle(handler) {
    const { onFulfilled, onRejected, resolve, reject } = handler;
    try {
      if (this._state === FULFILLED) {
        if (typeof onFulfilled === "function") {
          resolve(onFulfilled(this._value));
        } else {
          resolve(this._value);
        }
      } else if (this._state === REJECTED) {
        if (typeof onRejected === "function") {
          resolve(onRejected(this._value));
        } else {
          reject(this._value);
        }
      }
    } catch (e) {
      reject(e);
    }
  }

  then(onFulfilled, onRejected) {
    return new Promise((resolve, reject) => {
      const handler = { onFulfilled, onRejected, resolve, reject };
      this._handlers.push(handler);
      this._flushHandlers();
    });
  }

  catch(onRejected) {
    return this.then(undefined, onRejected);
  }

  finally(onFinally) {
    if (typeof onFinally !== "function") {
      return this.then();
    }
    return this.then(
      (value) => Promise.resolve(onFinally()).then(() => value),
      (reason) => Promise.resolve(onFinally()).then(() => { throw reason; })
    );
  }

  // --- Static helpers ---

  static resolve(value) {
    if (value instanceof Promise) {
      return value;
    }
    return new Promise((resolve) => resolve(value));
  }

  static reject(reason) {
    return new Promise((_, reject) => reject(reason));
  }

  static all(iterable) {
    return new Promise((resolve, reject) => {
      const results = [];
      let remaining = 0;
      let i = 0;
      for (const item of iterable) {
        const index = i++;
        remaining++;
        Promise.resolve(item).then(
          (v) => {
            results[index] = v;
            if (--remaining === 0) {
              resolve(results);
            }
          },
          (e) => reject(e)
        );
      }
      if (i === 0) {
        resolve([]);
      }
    });
  }

  static race(iterable) {
    return new Promise((resolve, reject) => {
      for (const item of iterable) {
        Promise.resolve(item).then(resolve, reject);
      }
    });
  }

  static allSettled(iterable) {
    return new Promise((resolve) => {
      const results = [];
      let remaining = 0;
      let i = 0;
      for (const item of iterable) {
        const index = i++;
        remaining++;
        Promise.resolve(item).then(
          (v) => {
            results[index] = { status: "fulfilled", value: v };
            if (--remaining === 0) resolve(results);
          },
          (e) => {
            results[index] = { status: "rejected", reason: e };
            if (--remaining === 0) resolve(results);
          }
        );
      }
      if (i === 0) {
        resolve([]);
      }
    });
  }

  static any(iterable) {
    return new Promise((resolve, reject) => {
      const errors = [];
      let remaining = 0;
      let i = 0;
      for (const item of iterable) {
        const index = i++;
        remaining++;
        Promise.resolve(item).then(
          (v) => resolve(v),
          (e) => {
            errors[index] = e;
            if (--remaining === 0) {
              reject(new AggregateError(errors, "All promises were rejected"));
            }
          }
        );
      }
      if (i === 0) {
        reject(new AggregateError([], "All promises were rejected"));
      }
    });
  }
}

globalThis.Promise = Promise;


