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

"""Functional data types to use in lieu of exceptions."""

from __future__ import annotations

__all__ = [ 'MB', 'XOR', 'mb_to_xor', 'xor_to_mb' ]
__author__ = "Geoffrey R. Scheller"
__copyright__ = "Copyright (c) 2023-2024 Geoffrey R. Scheller"
__license__ = "Apache License 2.0"

from typing import Callable, Generic, Iterator, Optional, TypeVar

_T = TypeVar('_T')
_S = TypeVar('_S')
_L = TypeVar('_L')
_R = TypeVar('_R')

class MB(Generic[_T]):
    """Class representing a potentially missing value.

    * implements the Maybe Monad
    * where MB(value) contains a possible value of type _T
    * MB( ) semantically represent "Nothing"
    * therefore None, as a value, cannot be put into a MB
    * immutable - a MB does not change after being created
    * immutable - map & flatMap produce new instances
    """
    __slots__ = '_value',

    def __init__(self, value: Optional[_T]=None):
        self._value = value

    def __iter__(self) -> Iterator[_T]:
        """Yields its value if not a "Nothing"."""
        if self._value is not None:
            yield self._value

    def __repr__(self) -> str:
        if self:
            return 'MB(' + repr(self._value) + ')'
        else:
            return 'MB()'

    def __bool__(self) -> bool:
        """Determine if the `MB` contains a value.

        * return `True` if the `MB` contains a value
        * return `False` otherwise
        """
        return self._value is not None

    def __len__(self) -> int:
        if self._value is None:
            return 0
        else:
            return 1

    def __eq__(self, other: object) -> bool:
        """Return `True` only when

        * both sides are "Nothings"
        * both sides contain values which compare as equal
        """
        if not isinstance(other, type(self)):
            return False
        return self._value == other._value

    def get(self, alt: Optional[_T]=None) -> Optional[_T]:
        """Get contents if they exist

        * otherwise return an alternate value of type `_T|NoneType`
        * alternate value defaults to `None`
        """
        if self._value is None:
            return alt
        else:
            return self._value

    def map(self, f: Callable[[_T], Optional[_S]]) -> MB[_S]:
        """Map `f` over the 0 or 1 elements of the data structure."""
        if self._value is None:
            return MB()
        return MB(f(self._value))

    def flatmap(self, f: Callable[[_T], MB[_S]]) -> MB[_S]:
        """Map `f` and flatten."""
        if self._value is None:
            return MB()
        return f(self._value)

class XOR(Generic[_L, _R]):
    """Class that either contains a "left" value or "right" value, but not both.

    * implements a left biased Either Monad
    * semantically containing 1 of 2 possible types of values
    * XOR(left: _L, right: _R) produces "left" value
    * XOR(None, right: _R) produces a "right" value
    * therefore None as a value, not implementation detail, can't be put into a "left"
    * in a Boolean context, returns `True` if a "left", `False` if a "right"
    * immutable, an `XOR` does not change after being created
    * immutable semantics, `map` & `flatMap` never mutate `self`
    """
    __slots__ = '_left', '_right'

    def __init__(self, potential_left: Optional[_L], default_right: _R):
        self._left, self._right = potential_left, default_right

    def __bool__(self) -> bool:
        """Predicate to determine if the `XOR` contains a "left" or a "right".

        * true if the XOR is a "left"
        * false if the XOR is a "right"
        """
        return self._left is not None

    def __iter__(self) -> Iterator[_L]:
        """Yields its value if the XOR is a "left"."""
        if self._left is not None:
            yield self._left

    def __repr__(self) -> str:
        return 'XOR(' + repr(self._left) + ', ' + repr(self._right) + ')'

    def __len__(self) -> int:
        """Semantically, an `XOR` always contains just one value."""
        return 1

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return False

        if self and other:
            return self._left == other._left
        elif not self and not other:
            return self._right == other._right
        else:
            return False

    def get(self, alt: Optional[_L]=None) -> Optional[_L]:
        """Get value if a Left.

        * if the XOR is a left, return its value
        * otherwise, return alt if it is not None
        * otherwise, return None
        """
        if self._left is None:
            return alt
        else:
            return self._left

    def getRight(self, alt: Optional[_R]=None) -> Optional[_R]:
        """Get value if a Right.

        * if XOR is a right, return its value
        * otherwise return an alternate value of type `_R|NoneType`
        * default alternate value is None
        """
        if self._left is None:
            return self._right
        else:
            return alt

    def map(self, f: Callable[[_L], Optional[_S]], right: Optional[_R]=None) -> XOR[_S, _R]:
        """Map over an `XOR`.

        * if a "left" apply f and return a "left" if f successful
        * otherwise, if f unsuccessful, return a "right" with non-None right
        * otherwise, if right None, return a "right" with the default right value
        * if a "right" return a  "right" with non-None right
        * otherwise, if right None, propagate the "right"
        """
        if self._left is None:
            if right is None:
                return XOR(None, self._right)
            else:
                return XOR(None, right)
        else:
            if right is None:
                return XOR(f(self._left), self._right)
            else:
                return XOR(f(self._left), right)

    def mapRight(self, g: Callable[[_R], _R]) -> XOR[_L, _R]:
        """Map over a "right" value."""
        if self._left is None:
            return XOR(None, g(self._right))
        return self

    def flatMap(self, f: Callable[[_L], XOR[_S, _R]]) -> XOR[_S, _R]:
        """Map and flatten a `Left` value, propagate `Right` values."""
        if self._left is None:
            return XOR(None, self._right)
        else:
            return f(self._left)

# Conversion functions

def mb_to_xor(m: MB[_T], right: _R) -> XOR[_T, _R]:
    """Convert a `MB` to an `XOR`."""
    return XOR(m.get(), right)

def xor_to_mb(e: XOR[_T,_S]) -> MB[_T]:
    """Convert an `XOR` to a `MB`."""
    return MB(e.get())

if __name__ == "__main__":
    pass
