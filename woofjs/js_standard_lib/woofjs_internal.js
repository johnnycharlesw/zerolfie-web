// This file defines to WoofJS how to decipher JS syntax

// General details
__WoofJS__.setSyntaxStyle(__WoofJS__.CStyleSyntax);
__WoofJS__.booleanKeywords = {
    "true":__WoofJS__.booleanKeywords.true,
    "false":__WoofJS__.booleanKeywords.false
};
__WoofJS__.allowJSLikeBlockFunctions=true;
__WoofJS__.variableKeywords={
    "const": __WoofJS__.variableDefinitions.NonOverwritable,
    "let": __WoofJS__.variableDefinitions.Overwritable.FunctionScoped,
    "var": __WoofJS__.variableDefinitions.Overwritable.BlockScoped,
};
__WoofJS__.functionKeywords={
    "function": __WoofJS__.functionDefinition,
    "async": __WoofJS__.asynchronous,
};

// Functions
const __WoofJS_DefineFunction=(body,params)=>{
    return new Function(...params,body);
}

let __WoofJS_DefineAsyncFunction=(body,params)=>{
    return new AsyncFunction(...params,body);
}

let __WoofJS_DefineNamedFunction=(name,body,params)=>{
    globalThis[name]=__WoofJS_DefineFunction(body, params);
}

function __woofJS_exponent(x,y){
    let result=x;
    for (let i = 0; i < y; i++) {
        result=result*y;
        
    }
    return result;
}

__WoofJS__.operatorHandlers = {
    "+":__WoofJS__.add,
    "-":__WoofJS__.subtract,
    "*": __WoofJS__.multiply,
    "/": __WoofJS__.divide,
    "%":__WoofJS__.remainder,
    "**": __woofJS_exponent
};