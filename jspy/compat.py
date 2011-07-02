# Compatibility layer over some python stdlib modules


__all__ = (
    'unittest',
)

import sys

try:
    import unittest2 as unittest
except ImportError:
    if sys.version_info >= (2, 7):
        import unittest
    else:
       raise
