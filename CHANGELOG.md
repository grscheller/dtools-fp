# CHANGELOG

PyPI grscheller.fp project.

#### Semantic versioning

* first digit
  * major event, epoch, or paradigm shift
* second digit
  * breaking API changes
  * major changes
* third digit
  * API additions
  * bug fixes
  * minor changes
  * significant documentation updates
  * breaking API or major changes (development environment only)
* forth digit (development environment only)
  * commit count of "non-trivial" changes/regressions

## Releases and Important Milestones

### Version 1.0.0 - PyPI Release: 2024-10-18

* decided to make this release first stable release
* renamed module fp.woException to fp.err\_handling
  * better captures module's use case
* pytest improvements based on pytest documentation

### Version 0.4.0 - PyPI Release: 2024-10-03

* long overdue PyPI release

### Version 0.3.5.1 - Commit Date: 2024-10-03

* New module `grscheller.fp.nothingness` for
  * Singleton `noValue` representing a missing value
    * similar to `None` but while
      * `None` represent "returned no values"
      * `noValue: _NoValue = _NoValue()` represents an absent value
    * mostly used as an implementation detail
      * allows client code to use `None` as a sentinel value
    * prefer class `MB` to represent a missing value in client code

### Version 0.3.4.0 - Commit Date: 2024-09-30

* API change for fp.iterables
  * function name changes
    * `foldL`, `foldR`, `foldLsc`, `foldRsc`
    * `sc` stands for "short circuit"
  * all now return class woException.MB

### Version 0.3.3.7 - Commit Date: 2024-09-22

* added more functions to fp.iterables module
  * take(it: Iterable[D], n: int) -> Iterator[D]
  * takeWhile(it: Iterable[D], pred: Callable[[D], bool]) -> Iterator[D]
  * drop(it: Iterable[D], n: int) -> Iterator[D]
  * dropWhile(it: Iterable[D], pred: Callable[[D], bool]) -> Iterator[D]

### Version 0.3.3.4 - Commit Date: 2024-09-16

* fp.iterables `foldL_sc` & `foldR_sc` now have
  * common paradigm
  * similar signatures

### Version 0.3.3.3 - Commit Date: 2024-09-15

* added fp.iterables function `foldR_sc`
  * shortcut version of `foldR`
  * not fully tested
  * docstring not updated

### Version 0.3.3.2 - Commit Date: 2024-09-14

* added fp.iterables function `foldL_sc`
  * shortcut version of foldL

### Version 0.3.3 - PyPI Release: 2024-08-25

* removed woException `XOR` method 
  * `getDefaultRight(self) -> R`:
* added methods
  * makeRight(self, right: R|Nada=nada) -> XOR[L, R]:
  * swapRight(self, right: R) -> XOR[L, R]:

### Version 0.3.1 - PyPI Release: 2024-08-20

* fp.iterables no longer exports `CONCAT`, `MERGE`, `EXHAUST`
  * for grscheller.datastructures
    * grscheller.datastructures.ftuple
    * grscheller.datastructures.split\_ends

### Version 0.3.0 - PyPI Release: 2024-08-17

* class Nothing re-added but renamed class Nada
  * version grscheller.untyped.nothing for more strictly typed code

### Version 0.2.1 - PyPI Release: 2024-07-26

PyPI grscheller.fp package release v0.2.1

* forgot to update README.md on last PyPI release
* simplified README.md to help alleviate this mistake in the future

### Version 0.2.0 - PyPI Release: 2024-07-26

* from last PyPI release
  * added accumulate function to fp.iterators
  * new fp.nothing module implementing nothing: Nothing singleton
    * represents a missing value
    * better "bottom" type than either None or ()
  * renamed fp.wo_exception to fp.woException
* overall much better docstrings

### Version 0.1.0 - Initial PyPI Release: 2024-07-11

* replicated functionality from grscheller.datastructures
  * grscheller.datastructures.fp.MB  -> grscheller.fp.wo\_exception.MB
  * grscheller.datastructures.fp.XOR -> grscheller.fp.wo\_exception.XOR
  * grscheller.core.iterlib          -> grscheller.fp.iterators
