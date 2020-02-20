"""
Demo flower using cython
=========================

Defines the Kivy garden :class:`CythonFlowerLabel` class which is
the widget provided by the demo cython flower.
"""

from kivy.uix.label import Label
from ._version import __version__
from ._compute import compute

__all__ = ('CythonFlowerLabel', )


class CythonFlowerLabel(Label):

    def __init__(self, **kwargs):
        val = compute('Demo flower', 2)
        super(CythonFlowerLabel, self).__init__(**kwargs, text=val)
