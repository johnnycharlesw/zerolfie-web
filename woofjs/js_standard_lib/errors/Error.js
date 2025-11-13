// Base Error class
class ErrorConstructor {
  #_isError=true;
  
  constructor(message = '') {
    this.name = 'Error';
    this.message = String(message);
    // capture stack from host if available
    this.stack = __WoofJS__.captureStack?.() ?? '';
  }

  toString() {
    const name = this.name ?? 'Error';
    const message = this.message ?? '';
    if (!name) return message;
    if (!message) return name;
    return `${name}: ${message}`;
  }

  isError(e){
    return Boolean(e._isError);
  }

  captureStackTrace(object, constructor){
    return __WoofJS__.Error_captureStackTrace(this, object, constructor);
  }
}

// Expose globally
__global__.Error = ErrorConstructor;