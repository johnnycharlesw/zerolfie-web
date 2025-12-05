// Tests for functions

function printStatusCheck(testName, status) {
    if (status) {
        console.log(testName + " status: OK");
    } else {
        console.log(testName + " status: FAIL");
    }
}

printStatusCheck("Function definition and call", true);


// Tests for regular stuff

printStatusCheck("\"console\" object support", (typeof console !== 'undefined'));

// Test for variable declaration and assignment
let x;
printStatusCheck("Variable declaration", (typeof x !== 'undefined' && x == null));
x = 1+1;
printStatusCheck("Variable assignment", (x == 2));

// Test static variable declaration and assignment
const staticVar=42;
try {
    staticVar=100;
    printStatusCheck("Static variable reassignment blocked", false);
}
catch (e) {
    printStatusCheck("Static variable reassignment blocked", true);
}

// Test for anonymous functions
printStatusCheck("Anonymous function", (()=>{ return true; })())

// Tests for arithmetic operations
printStatusCheck("Addition", (1+1==2));
printStatusCheck("Subtraction", (5-3==2));
printStatusCheck("Multiplication", (4*2==8));
printStatusCheck("Division", (9/3==3));
printStatusCheck("Modulus", (10%3==1));
printStatusCheck("Exponentiation", (2**3==8));



// Tests for obscure syntax

/*
Obscure method of writing:
console.log(1);
console.log(2);
console.log(3);
*/

[1, 2, 3].forEach(number => {
    console.log(number);
});

/* 
Obscure method of writing:
function printHelloWorld() {
    console.log("Hello World!")
}
printHelloWorld();
*/

let printHelloWorld = () => {
    console.log("Hello World!");
}
try {
    printHelloWorld();
    printStatusCheck("Arrow function definition and call", true);
}
catch (e) {
    printStatusCheck("Arrow function definition and call", false);
}

// WoofJS API is internal, but this is a userspace test file, so we should not be able to access it.
try {
    if (__WoofJS__) printStatusCheck("WoofJS API is not accessible in userspace", false);
} catch (e) {
    printStatusCheck("WoofJS API is not accessible in userspace", true);
}

// ASI check
printStatusCheck("Automatic semicolon insertion", true)