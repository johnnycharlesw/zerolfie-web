// Generator.js
class Generator extends Iterator {
    throw(err) { throw err; }
    return(value) { return { value, done: true }; }
  }
  globalThis.Generator = Generator;
  
