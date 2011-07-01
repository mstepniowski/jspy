jspy - JavaScript interpreter in Python
=======================================

*jspy* is a toy JavaScript interpreter in Python created by Marek Stepniowski. Its implementation is directly based on [ECMA-262 standard (PDF)](http://www.ecma-international.org/publications/files/ECMA-ST/Ecma-262.pdf).


Usage
-----

First install the package:

<pre>
    $ cd /main/jspy/folder
    $ python setup.py install
</pre>

You may need to have root rights, depending on your system configuration. After the installation, `jspy` script should be on your path. You can then just run the script with the JavaScript file as a single argument:

<pre>
    $ jspy file.js
</pre>


Test suite
----------

Test suite requires Python 2.7 or later. If you have an older version of Python, you will need to install [unittest2](http://pypi.python.org/pypi/unittest2) package.

To run the tests:

<pre>
    $ cd /main/jspy/folder
    $ unit2 discover
</pre>


Source code
-----------

You can find the newest source code of *jspy* on [GitHub](https://github.com/zuber/jspy).


Implemented features
--------------------

  * Expressions (excluding `delete`, `typeof`, `instanceof` and `in` operators)
  * Statements (excluding `for` and `for in` loops, `with`, `switch`, labels and exception handling)
  * Functions (with nested execution scopes allowing for closures)

 
Todo (in order of priorities)
-----------------------------

  * `for` and `for in` loops
  * `switch` statement
  * Objects (including an implementation of `Array`)
  * `delete`, `typeof`, `instanceof` and `in` operators
  * Prototypal inheritance
  * Exception handling
  * Strict mode (should we run in strict mode by default?)
  * Labels for `break` and `continue` statements
  * `with` statement (it's evil!)

