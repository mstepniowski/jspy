#!/usr/bin/env python
from distutils.core import setup


setup(
    name='jspy',
    version='1.0',
    description='JavaScript interpreter in Python',
    author='Marek Stepniowski',
    author_email='marek@stepniowski.com',
    url='http://github.com/zuber/jspy',
    platforms='Cross Platform',
    classifiers=['License :: OSI Approved :: MIT License'],
    
    packages=['jspy', 'ply'],
    scripts=['scripts/jspy'],
)
