// Fundamental Boolean constructor/function for WoofJS.
// - Called as a function: Boolean(x) → primitive true/false
// - Called with new: new Boolean(x) → Boolean object wrapping a primitive

class __WoofJS_BooleanObject {
    constructor(value = false) {
      // Internal wrapped primitive
      this.__woofjs_value__ = !!value;
    }
  
    valueOf() {
      return this.__woofjs_value__;
    }
  
    toString() {
      return this.__woofjs_value__ ? "true" : "false";
    }
  }
  
  function Boolean(value = false) {
    // Function call: return primitive
    if (!new.target) {
      return !!value;
    }
    // Constructor call: return Boolean object
    return new __WoofJS_BooleanObject(value);
  }
  
  // Share methods between constructed Booleans
  Boolean.prototype = __WoofJS_BooleanObject.prototype;
  Boolean.prototype.constructor = Boolean;
  
  // Expose globally
  globalThis.Boolean = Boolean;