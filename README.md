# Developer Tools - Pythonic Functional Programming

Functional programming tools which endeavor to be Pythonic.

* **Repositories**
  * [dtools.fp][1] project on *PyPI*
  * [Source code][2] on *GitHub*
* Detailed documentation for dtools.fp
  * [Detailed API documentation][3] on *GH-Pages*

This project is part of the
[Developer Tools for Python][4] **dtools.** namespace project.

### Modules

* dtools.fp.err\_handling
  * monadic tools for handling missing values & unexpected events
* dtools.fp.function
  * utilities to manipulate and partially apply functions
* dtools.fp.iterables
  * iteration tools implemented in Python
* dtools.fp.lazy
  * lazy (non-strict) function evaluation
* dtools.fp.nothingness
  * singleton classes representing either a
    * missing value
    * sentinel value
    * failed calculation
* dtools.fp.state
  * pure FP handling of state (the state monad)

### Benefits of FP

* improved composability
* avoid exception driven code paths
* data sharing becomes trivial due to immutability

---

[1]: https://pypi.org/project/dtools.fp/
[2]: https://github.com/grscheller/dtools-fp/
[3]: https://grscheller.github.io/dtools-docs/fp/
[4]: https://github.com/grscheller/dtools-docs/

