class ObjectConstructor {
    #keys_ = [];
    #values_ = [];
    constructor(value = null) {
        if (new.target !== this.constructor) {
            return new.target(value);
        }
        if (value=null) {
            return {}
        } else {
            return value;
        }
    }

    keys(){
        return this.#keys_;
    }

    is(a,b){
        return a === b;
    }

    preventExtensions(object){
        __WoofJS__.preventExtensions(object);
    }
}

globalThis.Object=ObjectConstructor;