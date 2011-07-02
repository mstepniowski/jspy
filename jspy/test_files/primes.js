// Print first 20 prime numbers
var isPrime = function (n) {
    var i = 2;
    while (i * i <= n) {
        if (n % i === 0) {
            return false;
        }
        ++i;
    }
    return true;
};

var printPrimes = function (count) {
    var i = 0, n = 2;
    while (true) {
        if (isPrime(n)) {
            console.log(n);
            ++i;
            if (i >= count) {
                break;
            }
        }
        ++n;
    }
};

printPrimes(20);
