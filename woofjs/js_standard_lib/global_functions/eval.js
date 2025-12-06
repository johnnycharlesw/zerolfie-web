function eval(script) {
    if (script === undefined || script === null) {
      return script;
    }
    const src = String(script);
  
    // If you want to be extra safe inside WoofJS, you could restrict this further.
    const fn = Function('"use strict"; return (function(){ ' + src + ' })()');
    return fn();
  }