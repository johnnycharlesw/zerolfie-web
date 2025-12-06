class WebAssembly {
    constructor(){
        this.constructor = () => {
            throw new TypeError("WebAssembly is not a constructor.");
        }
    }

    Module = class Module {
        customSections(module = this, sectionName) {
            // type checks
            if (!(module instanceof WebAssembly.Module)) {
                throw new TypeError("WebAssembly.Module.customSections only works with actual modules.");
            }
            if (!(typeof sectionName === "string")) {
                throw new TypeError("WebAssembly.Module.");
            }
        }
    }

    Exception = class Exception {
        constructor(tag, payload, options = {
            "traceStack": false
        }){

        }
    }
}