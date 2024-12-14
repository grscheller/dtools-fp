# Copyright 2023-2024 Geoffrey R. Scheller
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""### Module fp.singletons - collection of singleton classes

Classes permitting at most only one instantiation. Safer, but not as performant,
than a non-exported module level global. Difficult, but not impossible, for
a typical end-user to exploit. Different versions tailored for different use
cases.

#### Singleton types:

* **class NoValue:** singleton instance representing the absence of a value
* **Class Sentinel:** singleton instances used as a "hidden" sentinel value
* **class Nada:** singleton instance representing & propagating failure

##### `NoValue` was designed as a None replacement

While `None` represents "returned no values," `NoValue()` represents the absence
of a value. Non-existing values should not be comparable to anything, even
themselves. End-users may use both `None` and `()` as sentinel values which
colliding with using either to represent "nothingness." 

---

##### `Sentinel` values used as hidden implementation details

* Here is another implementation for Sentinel:``
  * on GitHub: [taleinat/python-stdlib-sentinels](https://github.com/taleinat/python-stdlib-sentinels)
  * on PyPI: [Project: Sentinels](https://pypi.org/project/sentinels/)
  * see: [PEP 661](https://peps.python.org/pep-0661/)

Initially this one was somewhat close to mine and also enabled pickling.
Subsequently it was "enhanced" to allow sentinel values to be subclassed. My
implementation is substantially more simple, python implementation independent,
less Gang-of-Four OOP, and more Pythonic.

---

##### `Nada` propagates failure

Nada is a singleton representing & propagating failure. Failure just blissfully
propagates down "the happy path." For almost everything you do with it, it just
returns itself. The maintainer has not used this construct enough yet to
determine if it is a brilliant idea or a horrible blunder.
"""
from __future__ import annotations

__all__ = [ 'NoValue', 'Sentinel', 'Nada' ]

from collections.abc import Callable, Iterator
from typing import Any, Final, final

class NoValue():
    """Singleton class representing a missing value.

    * similar to `None` but
      * while `None` represents "returned no values"
      * `NoValue()` represents the absence of a value
    * usage
      * `import NoValue from grscheller.fp.err_handling` and then
        * either use `NoValue()` directly
        * or define `_noValue: Final[NoValue] = NoValue()` don't export it
      * compare using `is` and `is not`
        * not `==` or `!=`
        * `None` means returned no values, so `None == None` makes sense
        * if one or both values are missing, then what is there to compare?

    """
    __slots__ = ()
    _instance: NoValue|None = None

    def __new__(cls) -> NoValue:
        if cls._instance is None:
            cls._instance = super(NoValue, cls).__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        return

    def __repr__(self) -> str:
        return 'NoValue()'

    def __eq__(self, other: object) -> bool:
        return False

@final
class Sentinel():
    """Singleton classes representing a sentinel values.

    * intended for library code, not to be exported/shared between modules
      * otherwise some of its intended typing guarantees may be lost
    * useful substitute for `None` as a hidden sentinel value
      * allows `None` to be stored in data structures
      * allows end users to choose to use `None` or `()` as sentinel values
      * always equals itself (unlike `noValue`)
    * usage
      * import Sentinel and then either
        * define `_my_sentinel: Final[Sentinel] = Sentinel('my_sentinel')`
        * or use `Sentinel('my_sentinel')` directly
      * compare using either
        * `is` and `is not` or `==` and `!=`
        * the `Sentinel()` value always equals itself
        * and never equals anything else, especially other sentinel values

    """
    __slots__ = '_sentinel_name',
    _instances: dict[str, Sentinel] = {}

    def __new__(cls, sentinel_name: str) -> Sentinel:
        if sentinel_name not in cls._instances:
            cls._instances[sentinel_name] = super(Sentinel, cls).__new__(cls)
        return cls._instances[sentinel_name]

    def __init__(self, sentinel_name: str) -> None:
        self._sentinel_name = sentinel_name
        return

    def __repr__(self) -> str:
        return "Sentinel('" + self._sentinel_name + "')"

@final
class Nada():
    """Singleton class representing & propagating failure.

    * singleton `_nada: nada = Nada()` represents a non-existent value
    * returns itself for arbitrary method calls
    * returns itself if called as a Callable with arbitrary arguments
    * interpreted as an empty container by standard Python functions
    * warning: non-standard equality semantics
      * comparison compares true only when 2 non-missing values compare true
      * thus `a == b` means two non-missing values compare as equal
    * usage
      * import `Nada` and then
        * either use `Nada()` directly
        * or define `_nada: Final[Nada] = Nada()` don't export it
      * start propagating failure by setting a propagating value to Nada()
        * works best when working with expression
        * failure may fail to propagate
          * for a function/method with just side effects
          * engineer Nada() to fail to trigger side effects
      * test for failure by comparing a result to `Nada()` itself using
        * `is` and `is not`
      * propagate failure through a calculation using
        * `==` and `!=`
        * the `Nada()` value never equals itself
        * and never equals anything else

    """
    __slots__ = ()
    _instance: Nada|None = None
    _hash: int = 0

    sentinel: Final[Sentinel] = Sentinel('Nada')

    def __new__(cls) -> Nada:
        if cls._instance is None:
            cls._instance = super(Nada, cls).__new__(cls)
            cls._hash = hash((cls._instance, (cls._instance,)))
        return cls._instance

    def __iter__(self) -> Iterator[Any]:
        return iter(())

    def __hash__(self) -> int:
        return self._hash

    def __repr__(self) -> str:
        return 'Nada()'

    def __bool__(self) -> bool:
        return False

    def __len__(self) -> int:
        return 0

    def __add__(self, right: Any) -> Nada:
        return Nada()

    def __radd__(self, left: Any) -> Nada:
        return Nada()

    def __mul__(self, right: Any) -> Nada:
        return Nada()

    def __rmul__(self, left: Any) -> Nada:
        return Nada()

    def __eq__(self, right: Any) -> bool:
        return False

    def __ne__(self, right: Any) -> bool:
        return True

    def __ge__(self, right: Any) -> bool:
        return False

    def __gt__(self, right: Any) -> bool:
        return False

    def __le__(self, right: Any) -> bool:
        return False

    def __lt__(self, right: Any) -> bool:
        return False

    def __getitem__(self, index: int|slice) -> Any:
        return Nada()

    def __setitem__(self, index: int|slice, item: Any) -> None:
        return

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return Nada()

    def __getattr__(self, name: str) -> Callable[..., Any]:
        def method(*args: tuple[Any], **kwargs: dict[str, Any]) -> Any:
            return Nada()
        return method

    def nada_get(self, alt: Any=sentinel) -> Any:
        """Get an alternate value, defaults to `Nada()`."""
        if alt == Sentinel('Nada'):
            return Nada()
        else:
            return alt

