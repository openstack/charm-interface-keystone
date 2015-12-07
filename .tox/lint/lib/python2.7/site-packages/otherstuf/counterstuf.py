"""
Sidecar to `stuf` that adds `Counter`-like
container `counterstuf`
"""
try:
    from collections import Counter
except ImportError:
    from stuf.collects import Counter

class counterstuf(Counter):
    """stuf-like surfacing of Counter"""

    def __getattr__(self, key):
        return self[key]

    def __setattr__(self, key, value):
        self[key] = value

    def update_self(self, *args, **kwargs):
        self.update(*args, **kwargs)
        return self

    def copy(self):
        return counterstuf(Counter.copy(self))
