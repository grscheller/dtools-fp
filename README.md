# PyPI grscheller.fp Project

Python package to facilitate functional programming in a pythonic way.

* Functional & imperative programming styles supported
* FP supported but project endeavors to remain Pythonic
* Methods which mutate objects don't return anything
* [grscheller.fp][1] project on PyPI
* [Detailed API documentation][2] on GH-Pages
* [Source code][3] on GitHub

## Overview

This package does not force functional programming paradigms on client
code, but provide functional tools to opt into.

### Some of the main benefit of the functional programming style are:

* avoid unnecessary exception driven code paths upon client code
* data sharing becomes trivial due to immutability

### Modules provided

* module grscheller.fp.wo\_exception
  * class `MB[T]`
    * the maybe monad
    * represents a potentially missing value
      * result of a calculation that could fail
      * user input which could be missing
  * class `XOR[L,R]`
    * the either monad
    * one of two possible exclusive categories of values
    * either one or the other, not both
    * left biased
* module grscheller.fp.iterators
  * Combining multiple iterators
    * *function* `concat(*t)`
      * DEPRECATED - use itertools.chain instead
      * sequentially concatenate multiple iterables
      * still performant
      * proof of concept
    * *function* `merge(*t)`
      * merge iterables until one is exhausted
    * *function* `exhaust(*t)`
      * merge iterables until all are exhausted

---

[1]: https://pypi.org/project/grscheller.fp/
[2]: https://grscheller.github.io/fp/API/development/html/grscheller/datastructures/index.html
[3]: https://github.com/grscheller/fp/
