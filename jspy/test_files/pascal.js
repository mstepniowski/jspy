// Prints the first 10 rows of [Pascal's triangle](http://en.wikipedia.org/wiki/Pascal%27s_triangle)
var sierpinski = function(rowCount) {
    var row = [1], length = 1, i = 0;
    var nextRow = function() {
        var result = [1], i = 0;
        while (i < length - 1) {
            result[i + 1] = row[i] + row[i + 1];
            ++i;
        }
        result[i + 1] = 1;
        return result;
    };

    while (i < rowCount) {
        console.log(row);
        row = nextRow();
        ++length;
        ++i;
    }
};

sierpinski(10);
