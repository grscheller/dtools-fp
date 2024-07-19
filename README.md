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

* [grscheller.fp.bottom](#grschellerfpbottom)
* [grscheller.fp.iterators](#grschellerfpiterators)
* [grscheller.fp.woException](#grschellerfpwoexception)

### grscheller.fp.bottom
  * class Opt[T](t: Optional[T])
    * implements an Optional/Maybe Monad with a "bottom value" Opt()
    * semantically represents a value of type _T|None
    * delegates most standard functions/methods to the contained object, if it exists
    * get_, map_, flatMap_ and some inherited from object act on the Opt container
    * use map_(lambda x: x.foobar()) to access specific methods of contained object
    * use map to perform a map on the underlying object
    * Opt() is a better "bottom" type than either None or ()
    * Opt() not a singleton, so use == and != instead of "is" and "is not"
    * Opt[NoneType] by design is unrepresentable

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

### grscheller.fp.woException
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

[1]: https://pypi.org/project/grscheller.fp/
[2]: https://grscheller.github.io/fp/
[3]: https://github.com/grscheller/fp/
