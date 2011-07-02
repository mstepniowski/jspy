// Generates Fibonacci numbers from F_0 to F_20
var fibgen = function () {
    var a = 0, b = 1;
    return function () {
        var old = a;
        a = b;
        b = b + old;
        return old;
    };
};

var fibonacciNumbers = [], count = 21, i = 0, fib = fibgen();

while (i < count) {
    fibonacciNumbers[i] = fib();
    ++i;
}
