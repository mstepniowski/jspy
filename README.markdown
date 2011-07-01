jspy - JavaScript interpreter in Python
=======================================

*jspy* is a toy JavaScript interpreter in Python created by Marek Stepniowski. Its implementation is directly based on [ECMA-262 standard (PDF)](http://www.ecma-international.org/publications/files/ECMA-ST/Ecma-262.pdf).


Test suite
----------

Test suite requires Python 2.7 or later. If you have an older version of Python, you will need to install [unittest2](http://pypi.python.org/pypi/unittest2) package.

To run the tests:

<pre>
    # cd /main/jspy/folder
    # unit2 discover
</pre>


Implemented features
--------------------

  * Expressions (excluding `delete`, `void`, `typeof`, `instanceof` and `in` operators)
  * Statements (excluding `for` loop, `with`, `switch`, labels, exception handling and `debugger`)

Still todo
----------

  * `delete`, `void`, `typeof`, `instanceof` and `in` operators
  * `for` loop, `with`, `switch`, labels, exception handling and `debugger`)
  * Objects
  * Prototypal inheritance

