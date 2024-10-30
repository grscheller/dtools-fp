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

"""### Maybe and Either Monads.

Monadic functional data types to use in lieu of exceptions.

##### Monadic types:

* **MB:** Maybe monad
* **XOR:** Left biased Either monad

"""
from __future__ import annotations

__all__ = [ 'MB', 'XOR', 'sequence_mb', 'sequence_xor' ]

from typing import Any, Callable, cast, Final, Iterator, List, Never, Self, Sequence
from .singletons import Sentinel

_sentinel: Final[Sentinel] = Sentinel()

class MB[D]():
    """#### Maybe Monad

    Class wrapping a potentially missing value.

    * where `MB(value)` contains a possible value of type `~D`
    * `MB()` semantically represent a non-existent or missing value of type `~D`
    * immutable, a `MB` does not change after being created
      * immutable semantics, map & flatMap return new instances
      * warning: contained values need not be immutable
      * warning: not hashable if a mutable value is contained
    * raises `ValueError` if get method not given default value & one is needed
    * implementation detail:
      * `MB( )` contains `fp.singleton.Sentinel()` as a sentinel value
        * as a result, a MB cannot semantically contain `Sentinel()` as a value

    """
    __slots__ = '_value',
    __match_args__ = ('_value',)

    def __init__(self, value: D|XOR[D,Any]|Sentinel=_sentinel) -> None:
        match value:
            case XOR(left, _):  # type: ignore # this should have worked due to __future__ import???
                self._value = left
            case data:
                self._value = data

    def __bool__(self) -> bool:
        return self._value is not _sentinel

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
        elif self._value == other._value:
            return True
        else:
            return False

    def get(self, alt: D|Sentinel=_sentinel) -> D|Never:
        """Return the contained value if it exists, otherwise an alternate value.

        * alternate value must me of type `~D`
        * raises `ValueError` if an alternate value is not provided but needed

        """
        if self._value is not _sentinel:
            return cast(D, self._value)
        else:
            if alt is not _sentinel:
                return cast(D, alt)
            else:
                msg = 'An alternate return type not provided.'
                raise ValueError(msg)

    def map[U](self, f: Callable[[D], U]) -> MB[U]:
        """Map function `f` over the 0 or 1 elements of this data structure."""
        return (MB(f(cast(D, self._value))) if self else MB())

    def flatmap[U](self, f: Callable[[D], MB[U]]) -> MB[U]:
        """Map `MB` with function `f` and flatten."""
        return (f(cast(D, self._value)) if self else MB())

class XOR[L,R]():
    """#### Either Monad

    Class semantically containing either a left or a right value, but not both.

    * implements a left biased Either Monad
      * `XOR(left: ~L, right: ~R)` produces a left value of type `~L`
        * with a default potential right value of type `~R`
      * `XOR(left)` produces a left value
      * `XOR(right=right)` produces a right value
    * in a Boolean context `True` if a left, `False` if a right
    * two `XOR` objects compare as equal when
      * both are left values or both are right values which
        * contain the same value or
        * whose values compare as equal
    * immutable, an `XOR` does not change after being created
      * immutable semantics, map & flatMap return new instances
      * warning: contained values need not be immutable
      * warning: not hashable if value or potential right value mutable
    * `get` and `getRight` methods can raises `ValueError` when
      * a right value is needed but a potential right value was not given

    """
    __slots__ = '_left', '_right'
    __match_args__ = ('_left', '_right')

    def __init__(self,
                 left: L|MB[L]|Sentinel=_sentinel,
                 right: R|Sentinel=_sentinel) -> None:
        match left:
            case MB(l):
                self._left, self._right = l, right
            case l:
                self._left, self._right = l, right

    def __bool__(self) -> bool:
        return self._left is not _sentinel

    def __iter__(self) -> Iterator[L]:
        if self._left is not _sentinel:
            yield cast(L, self._left)

    def __repr__(self) -> str:
        if self._left is _sentinel:
            return 'XOR(right=' + repr(self._right) + ')'
        else:
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
            elif self._left == other._left:
                return True
            else:
                return False

        if not self and not other:
            if self._right is other._right:
                return True
            elif self._right == other._right:
                return True
            else:
                return False

        return False

    def get(self, alt: L|Sentinel=_sentinel) -> L|Never:
        """Get value if a left.

        * if the `XOR` is a left, return its value
        * otherwise, return `alt: ~L` if it is provided
        * alternate value must me of type `~L`
        * raises `ValueError` if an alternate value is not provided but needed

        """
        sent: Final[Sentinel] = _sentinel
        if self._left is sent:
            if alt is sent:
                msg = 'An alt return value was needed by get, but none was provided.'
                raise ValueError(msg)
            else:
                return cast(L, alt)
        else:
            return cast(L, self._left)

    def getRight(self, alt: R|Sentinel=_sentinel) -> R|Never:
        """Get value of `XOR` if a Right, potential right value if a left.

        * if XOR is a right, return its value
          * otherwise return a provided alternate value of type `~R`
        * if `XOR` is a left, return the potential right value
          * raises `ValueError` if a potential right value was not provided

        """
        if self:
            sentinel: Final[Sentinel] = _sentinel
            if alt is sentinel:
                if self._right is sentinel:
                    msg = 'A potential right was needed by get, but none was provided.'
                    raise ValueError(msg)
                else:
                    return cast(R, self._right)
            else:
                return cast(R, alt)
        else:
            return cast(R, self._right)

    def makeRight(self, right: R|Sentinel=_sentinel) -> XOR[L, R]:
        """Make right

        Return a new instance transformed into a right `XOR`. Change the right
        value to right if given.
        """
        if right is _sentinel:
            right = self.getRight()
        return cast(XOR[L, R], XOR(right=right))

    def swapRight(self, right: R) -> XOR[L, R]:
        """Swap in a new right value, returns a new instance with a new right
        (or potential right) value.
        """
        if self._left is _sentinel:
            return cast(XOR[L, R], XOR(right=right))
        else:
            return XOR(self.get(), right)

    def map[U](self, f: Callable[[L], U]) -> XOR[U, R]:
        """Map over if a left value.

        * if `XOR` is a left then map `f` over its value
          * if `f` successful return a left `XOR[S, R]`
          * if `f` unsuccessful return right `XOR`
            * swallows any exceptions `f` may throw
        * if `XOR` is a right
          * return new `XOR(right=self._right): XOR[S, R]`
          * use method `mapRight` to adjust the returned value

        """
        if self._left is _sentinel:
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

    def flatMap[U](self, f: Callable[[L], XOR[U, R]]) -> XOR[U, R]:
        """Flatmap - Monadically bind

        * map over then flatten left values
        * propagate right values

        """
        if self._left is _sentinel:
            return XOR(right=self._right)
        else:
            return f(cast(L, self._left))

def sequence_mb[D](seq_mb_d: Sequence[MB[D]]) -> MB[Sequence[D]]:
    """Sequence an indexable container of `MB[~D]`

    *if all the contained `MB` values in the container are not empty,
      * return a `MB` of a container containing the values contained
      * otherwise return an empty `MB`

    """
    l: List[D] = []

    for mb_d in seq_mb_d:
        if mb_d:
            l.append(mb_d.get())
        else:
            return MB()

    ds = cast(Sequence[D], type(seq_mb_d)(l))  # type: ignore # will be a subclass at runtime
    return MB(ds)

def sequence_xor[L,R](seq_xor_lr: Sequence[XOR[L,R]],
                      potential_right: R|Sentinel=_sentinel,
                      default_right: R|Sentinel=_sentinel) -> XOR[Sequence[L],R]:
    """Sequence an indexable container of `XOR[L, R]`

    * if all the `XOR` values contained in the container are lefts, then
      * return an `XOR` of the same type container of all the left values
      * setting the potential right to `potential_right` if given
    * if at least one of the `XOR` values contained in the container is a right,
      * return a right XOR containing the right value of the first right
      * if right does not contain an `~R`, return right containing `default_right`

    """
    l: List[L] = []

    for xor_lr in seq_xor_lr:
        if xor_lr:
            l.append(xor_lr.get())
        else:
            try:
                return XOR(right=xor_lr.getRight())
            except ValueError:
                return XOR(right=default_right)

    ds = cast(Sequence[L], type(seq_xor_lr)(l))  # type: ignore # will be a subclass at runtime
    if potential_right is _sentinel:
        return XOR(ds)
    else:
        return XOR(ds, potential_right)

