// control_abstraction_objects/Iterator.js
class Iterator {
    next() {
      // Spec: returns { value, done }, but base does nothing.
      return { value: undefined, done: true };
    }
  
    [Symbol.iterator]() {
      return this;
    }
  }
  
  globalThis.Iterator = Iterator;