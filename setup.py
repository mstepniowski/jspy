#!/usr/bin/env python
from distutils.core import setup


setup(
    name='librarian',
    version='1.3',
    description='Converter from WolneLektury.pl XML-based language to XHTML, TXT and other formats',
    author="Marek Stepniowski",
    author_email='marek@stepniowski.com',
    url='http://github.com/zuber/jspy',
    packages=['jspy', 'ply'],
    scripts=['scripts/jspy']
)
