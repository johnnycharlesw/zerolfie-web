class Number {
    #_WoofJS_value = 0;
    constructor(value){
        if (typeof value === "bigint"){
            this.#_WoofJS_value=value;
        } else{
            this.#_WoofJS_value=value;
        }
    }

    isFinite(number = this){
        return isFinite(number);
    }

    isNaN(number = this){
        return isNaN(number);
    }

    isInteger(num = this){
        return (num == Math.trunc(num));
    }
    
    toString(radix = 10){
        return __WoofJS__.convertNumberToString(this,radix);
    }
}