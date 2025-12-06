// AsyncIterator.js
class AsyncIterator {
    async next() {
      return { value: undefined, done: true };
    }
  
    [Symbol.asyncIterator]() {
      return this;
    }
  }
  
  globalThis.AsyncIterator = AsyncIterator;