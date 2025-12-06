class JSON {
    constructor(){
        throw new TypeError("The JSON class is not intended to be used to create objects.");
    }

    parse(string) {
<<<<<<< HEAD
        return __WoofJS__.parseJSON(string);
=======
        __WoofJS__.parseJSON(string)
>>>>>>> a639a9f0acb2e945d43bd8855ea344d1bc6d8d66
    }
}