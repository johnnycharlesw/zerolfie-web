class JSON {
    constructor(){
        throw new TypeError("The JSON class is not intended to be used to create objects.");
    }

    parse(string) {
        return __WoofJS__.parseJSON(string);
    }
}