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

"""### Maybe and Either Monads

Functional data types to use in lieu of exceptions.

##### Monadic types:

* **MB:** Maybe monad
* **XOR:** Left biased Either monad

"""
from __future__ import annotations

__all__ = [ 'MB', 'XOR', 'mb_to_xor', 'xor_to_mb' ]

from typing import Callable, cast, Final, Generic, Iterator, Never, TypeVar
from .nada import Nada, nada

D = TypeVar('D')
U = TypeVar('U')
L = TypeVar('L')
R = TypeVar('R')

class MB(Generic[D]):
    """#### Maybe Monad

    Class representing a potentially missing value.

    * where `MB(value)` contains a possible value of type `~T`
    * `MB( )` semantically represent a non-existent or missing value of type ~T
    * immutable, a MB does not change after being created
    * immutable semantics, map and flatMap produce new instances
    * implementation detail
      * `MB( )` contains `nada` as a sentinel value
        * as a result, a MB cannot semantically contain `nada`

    """
    __slots__ = '_value',

    def __init__(self, value: D|Nada=nada) -> None:
        self._value = value

    def __bool__(self) -> bool:
        return not self._value is nada

    def __iter__(self) -> Iterator[D]:
        if self:
            yield cast(D, self._value)

    def __repr__(self) -> str:
        if self:
            return 'MB(' + repr(self._value) + ')'
        else:
            return 'MB()'

    def __len__(self) -> int:
        return (1 if self else 0)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return False

        if self._value is other._value:
            return True
        return self._value == other._value

    def get(self, alt: D|Nada=nada) -> D|Never:
        """Return the contained value if it exists, otherwise an alternate value.

        * alternate value must me of type ~T
        * raises `ValueError` if an alternate value is not provided but needed

        """
        if self._value is not nada:
            return cast(D, self._value)
        else:
            if alt is not nada:
                return cast(D, alt)
            else:
                msg = 'An alternate return type not provided.'
                raise ValueError(msg)

    def map(self, f: Callable[[D], U]) -> MB[U]:
        """Map function f over the 0 or 1 elements of this data structure."""
        return (MB(f(cast(D, self._value))) if self else MB())

    def flatmap(self, f: Callable[[D], MB[U]]) -> MB[U]:
        """Map MB with function f and flatten."""
        return (f(cast(D, self._value)) if self else MB())

class XOR(Generic[L, R]):
    """#### Either Monad

    Class semantically containing either a "left" or a "right" value,
    but not both.

    * implements a left biased Either Monad
      * `XOR(left, right)` produces a "left" and default potential "right" value
      * `XOR(left)` produces a "left" value
      * `XOR(right=right)` produces a "right" value
    * in a Boolean context, returns True if a "left", False if a "right"
    * two `XOR` objects compare as equal when
      * both are left values or both are right values which
        * contain the same value or
        * whose values compare as equal
    * immutable, an `XOR` does not change after being created
      * immutable semantics, map & flatMap return new instances
      * warning: contained values need not be immutable
    * raises `ValueError` if
      * a "right" value is needed but a potential "right" value was not given

    """
    __slots__ = '_left', '_right'

    def __init__(self, left: L|Nada=nada, right: R|Nada=nada) -> None:
        self._left, self._right = left, right

    def __bool__(self) -> bool:
        return self._left is not nada

    def __iter__(self) -> Iterator[L]:
        if self._left is not nada:
            yield cast(L, self._left)

    def __repr__(self) -> str:
        return 'XOR(' + repr(self._left) + ', ' + repr(self._right) + ')'

    def __str__(self) -> str:
        if self:
            return '< ' + str(self._left) + ' | >'
        else:
            return '< | ' + str(self._right) + ' >'

    def __len__(self) -> int:
        # Semantically, an XOR always contains just one value.
        return 1

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return False

        if self and other:
            if self._left is other._left:
                return True
            return self._left == other._left
        elif not self and not other:
            if self._right is other._right:
                return True
            return self._right == other._right
        else:
            return False

    def get(self, alt: L|Nada=nada) -> L:
        """Get value if a Left.

        * if the XOR is a left, return its value
        * otherwise, return alt: L if it is provided
        * alternate value must me of type ~L
        * raises `ValueError` if an alternate value is not provided but needed

        """
        if self._left is nada:
            if alt is nada:
                msg = 'An alt return value was needed by get, but none was provided.'
                raise ValueError(msg)
            else:
                return cast(L, alt)
        else:
            return cast(L, self._left)

    def getRight(self, alt: R|Nada=nada) -> R:
        """Get value of `XOR` if a Right, potential right value if a left.

        * if XOR is a right, return its value
          * otherwise return a provided alternate value of type ~R
        * if XOR is a left, return the potential right value
          * raises `ValueError` if a potential right value was not provided

        """
        if self:
            if alt is nada:
                if self._right is nada:
                    msg = 'A potential right was needed by get, but none was provided.'
                    raise ValueError(msg)
                else:
                    return cast(R, self._right)
            else:
                return cast(R, alt)
        else:
            return cast(R, self._right)

    def makeRight(self, right: R|Nada=nada) -> XOR[L, R]:
        """Make right

        Return a new instance transformed into a right `XOR`. Change the right
        value to `right` if given.
        """
        if right is nada:
            right = self.getRight()
        return cast(XOR[L, R], XOR(right=right))

    def swapRight(self, right: R) -> XOR[L, R]:
        """Swap in a new right value, returns a new instance with a new right
        (or potential right) value.
        """
        if self._left is nada:
            return cast(XOR[L, R], XOR(right=right))
        else:
            return XOR(self.get(), right)

    def map(self, f: Callable[[L], U]) -> XOR[U, R]:
        """Map over if a left value.

        * if `XOR` is a "left" then map `f` over its value
          * if `f` successful return a left XOR[S, R]
          * if `f` unsuccessful return right `XOR`
            * swallows any exceptions `f` may throw
            * FUTURE TODO: create class that is a "wrapped" XOR(~T, Exception)
        * if `XOR` is a "right"
          * return new `XOR(right=self._right): XOR[S, R]`
          * use method mapRight to adjust the returned value

        """
        if self._left is nada:
            return cast(XOR[U, R], XOR(right=self._right))

        try:
            applied = f(cast(L, self._left))
        except Exception:
            return XOR(right=self._right)
        else:
            return XOR(applied, self._right)

    def mapRight(self, g: Callable[[R], R]) -> XOR[L, R]:
        """Map over a right or potential right value."""
        return XOR(self._left, g(cast(R, self._right)))

    def flatMap(self, f: Callable[[L], XOR[U, R]]) -> XOR[U, R]:
        """Flatmap - Monadically bind

        * map over then flatten left values
        * propagate right values

        """
        if self._left is nada:
            return XOR(nada, self._right)
        else:
            return f(cast(L, self._left))

# Conversion functions

def mb_to_xor(m: MB[D], right: R) -> XOR[D, R]:
    """Convert a MB to an XOR."""
    if m:
        return XOR(m.get(), right)
    else:
        return XOR(nada, right)

def xor_to_mb(e: XOR[D,U]) -> MB[D]:
    """Convert an XOR to a MB."""
    if e:
        return MB(e.get())
    else:
        return MB()
