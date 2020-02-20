kivy-garden demo of cython flower
==================================

[![Github Build Status](https://github.com/kivy-garden/cython_flower/workflows/Garden%20flower/badge.svg)](https://github.com/kivy-garden/cython_flower/actions)

A kivy garden flower that shows how to add flowers that requires cython compilation.

See https://kivy-garden.github.io/cython_flower/ for the rendered flower docs.

Please see the garden [instructions](https://kivy-garden.github.io) for how to use kivy garden flowers.

Flower information
-------------------

A kivy garden flower demo with cython code.

Install
---------

To install with pip::

    pip install kivy_garden.cython_flower

To build or re-build locally::

    PYTHONPATH=.:$PYTHONPATH python setup.py build_ext --inplace

Or to install as editable (package is installed, but can be edited in its original location)::

    pip install -e .

CI
--

Every push or pull request run the [GitHub Action](https://github.com/kivy-garden/flower/actions) CI.
It tests the code on various OS and also generates wheels that can be released on PyPI upon a
tag. Docs are also generated and uploaded to the repo as well as artifacts of the CI.

TODO
-------

* add your code

Contributing
--------------

Check out our [contribution guide](CONTRIBUTING.md) and feel free to improve the flower.

License
---------

This software is released under the terms of the MIT License.
Please see the [LICENSE.txt](LICENSE.txt) file.

How to release
===============

See the garden [instructions](https://kivy-garden.github.io/#makingareleaseforyourflower) for how to make a new release.
