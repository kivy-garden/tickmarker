import pytest


def test_cython_flower():
    from kivy_garden.cython_flower import CythonFlowerLabel
    label = CythonFlowerLabel()
    assert label.text == 'Demo flower' * 2
