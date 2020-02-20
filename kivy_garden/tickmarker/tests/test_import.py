import pytest


def test_import():
    from kivy.uix.slider import Slider
    from kivy_garden.tickmarker import TickMarker

    class TickSlider(Slider, TickMarker):
        pass
    slider = TickSlider()
