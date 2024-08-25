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
* forth digit (development environment only)
  * commit count of "non-trivial" changes/regressions
  * third digit now plays the role of the second

## Releases and Important Milestones

### Version 0.3.3 - PyPI Release: 2024-08-25

* removed method
  * getDefaultRight(self) -> R:
* added methods
  * makeRight(self, right: R|Nada=nada) -> XOR[L, R]:
  * swapRight(self, right: R) -> XOR[L, R]:

### Version 0.3.1 - PyPI Release: 2024-08-20

* fp.iterables no longer exports CONCAT, MERGE, EXHAUST
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
  * grscheller.datastructures.fp.MB  -> grscheller.fp.wo_exception.MB
  * grscheller.datastructures.fp.XOR -> grscheller.fp.wo_exception.XOR
  * grscheller.core.iterlib          -> grscheller.fp.iterators
