# Python Functional Programming (FP)

Functional programming tools which endeavor to be Pythonic.

## Overview

* Source code for the grscheller.fp PyPI Package
* [grscheller.fp][1] project on PyPI
* [Detailed API documentation][2] on GH-Pages
* [Source code][3] on GitHub

### Benefits of FP

* avoid exception driven code paths
* data sharing becomes trivial due to immutability

## Modules

* [grscheller.fp.wo_exception](#grschellerfpwoexception)
* [grscheller.fp.iterators](#grschellerfpiterators)

### grscheller.fp.wo\_exception
  * class `MB[T](t: Optional[T])`
    * the maybe monad
    * represents a potentially missing value
      * result of a calculation that could fail
      * user input which could be missing
  * class `XOR[L, R](left: Optional[L], right: R)`
    * the either monad
    * one of two possible exclusive categories of values
    * either one or the other, not both
    * left biased

---

### grscheller.fp.iterators
  * Functions for combining multiple iterators
    * function `concat(*t: [Iterable[T]]): Iterator[T]`
      * sequentially concatenate multiple iterables
      * you may want to use the standard lib's itertools.chain instead
      * still performant
    * function `exhaust(*t: [Iterable[T]]): Iterator[T]`
      * merge iterables until all are exhausted
    * function `merge(*t: [Iterable[T]]): Iterator[T]`
      * merge iterables until one is exhausted

---

[1]: https://pypi.org/project/grscheller.fp/
[2]: https://grscheller.github.io/fp/
[3]: https://github.com/grscheller/fp/
