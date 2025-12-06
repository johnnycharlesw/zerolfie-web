class Math { // Manufacture the calculator
    E = 2.718281828459045;
    PI = 3.141592653589793;
    LOG10E = 0.4342944819032518;
    LOG2E = 1.4426950408889634;
    LN10 = 2.302585092994046;
    LN2 = 0.6931471805599453;
    SQRT1_2 = 0.7071067811865476;
    SQRT2 = 1.4142135623730951;

    constructor(){
        this.constructor = ()=>{
            throw TypeError("Math is a builtin class that is not supposed to be used on objects.");
        }
    }

    exp(x){
        return this.pow(this.E, x);
    }
    expm1(x){
        return this.exp(x)-1;
    }

    pow(x,y){
        if (typeof(x) == "number" && typeof(y) == "number") {
            return x ** y;
        } else {
            throw new TypeError("Math.pow only accepts numbers");
        }
    }

    sin(x){
        if (x==NaN || x==Infinity) {
            return NaN;
        }
        return __WoofJS__.getSineOf(x);
    }

    cos(x){
        if (x==NaN || x==Infinity) {
            return NaN;
        }
        return __WoofJS__.getCosineOf(x);
    }

    acos(x){
        if (x==NaN || x==Infinity) {
            return NaN;
        }
        return __WoofJS__.getArcCosineOf(x);
    }

    cosh(x){
        return (this.exp(x)+this.exp(x))/2;
    }

    asin(x){
        if (x==NaN || x==Infinity) {
            return NaN;
        }
        return __WoofJS__.getArcSineOf(x);
    }

    asinh(x){
        return __WoofJS__.getHyperbolicArcSineOf(x);
    }

    atan(x){
        return __WoofJS__.getArcTangentOf(x);
    }

    atanh(x){
        return __WoofJS__.getHyperbolicArcTangentOf(x);
    }
    acosh(x){
        return __WoofJS__.getHyperbolicArcCosineOf(x);
    }

    sinh(x){
        return (this.exp(x)-this.exp(x))/2;
    }

    tanh(x){
        return this.sinh(x)/this.cosh(x);
    }

    atan2(y,x){
        return __WoofJS__.atan2(y,x);
    }

    tan(x){
        if (x==NaN || x==Infinity) {
            return NaN;
        }
        return __WoofJS__.getTangentOf(x);
    }

    cbrt(x){
        return __WoofJS__.cubeRoot(x);
    }

    sqrt(x){
        return __WoofJS__.squareRoot(x);
    }

    log(x){
        return __WoofJS__.log(x);
    }

    log1p(x){
        return this.log(1+x);
    }

    log2(x){
        log=this.log(x);
        return this._woofJS_convertBase(log, 2);
    }

    log10(x){
        log=this.log(x);
        return this._woofJS_convertBase(log,10);
    }

    fround(x){
        return __WoofJS__._64bitFloatTo32BitFloat(x);
    }

    round(x){
        return __WoofJS__.roundToNearestInteger(x);
    }

    abs(x){
        // The absolute value is the number's distance from 0
        if (this.sign(x)<0) {
            return this._woofJS_invert(x); // Distances are always positive, and a negative number's opposite is positive
        } else {
            return x;
        }
    }

    sign(x){
        if (x<0) {
            return -1;
        } else {
            return 1;
        }
    }

    floor(x){
        return __WoofJS__.roundToLowestCloseInteger(x);
    }

    ceil(x){
        return __WoofJS__.roundToHighestCloseInteger(x);
    }

    trunc(x){
        return __WoofJS__.truncateBeforeFractionalPart(x);
    }

    max(...values){
        if (values.includes(NaN)) {
            return NaN;
        }
        
        let largest=-Infinity;
        values.forEach(value => {
            if (value > largest){
                largest=value;
            }
        });
        return largest;
    }

    min(...values){
        if (values.includes(NaN)) {
            return NaN;
        }
        let smallest=Infinity;
        values.forEach(value => {
            if (value < smallest){
                smallest=value;
            }
        });
        return smallest;
    }

    random(){
        return __WoofJS__.getRandomFraction();
    }

    clz32(x){
        return __WoofJS__.countLeadingZeros32(x);
    }

    imul(a,b){
        return __WoofJS__.multiply32BitIntegers(a,b);
    }

    sumPrecise(numbers){
        let sum=0;
        let c=0;
        // Approximation, please fix later
        numbers.forEach((number)=>{
            const y = x - c;
            const t = sum + y;
            c = (t-sum)-y;
            sum=t;
        });

        return sum;
    }

    f16round(doubleFloat){
        return __WoofJS__.roundToNearest16BitHalfPrecision(doubleFloat);
    }


    _woofJS_convertBase(x,base){
        return parseInt(x.toString(),base);
    }

    _woofJS_invert(num){
        return 0 - num;
    }

    __woofJS_unexponent(exponented,x,y){
        let unexponented=exponented;
        for (let i=0; i<y; i++){
            unexponented=unexponented/x;
        }
        return unexponented;
    }

    
}

globalThis.Math = Object.freeze(new Math()); // Throw the calculator into globalThis