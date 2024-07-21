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
from .nothing import Nothing

_T = TypeVar('_T')
_S = TypeVar('_S')
_L = TypeVar('_L')
_R = TypeVar('_R')

class MB(Generic[_T]):
    """Class representing a potentially missing value.

    * where MB(value) contains a possible value of type _T
    * MB( ) semantically represent a "Nothing" of type Bottom
    * therefore bottom = Bottom(), as a value, cannot be put into a MB
    * immutable - a MB does not change after being created
    * immutable semantics - map & flatMap produce new instances

    """
    __slots__ = '_value',

    def __init__(self, value: _T|Nothing=Nothing()) -> None:
        self._value = value

    def __iter__(self) -> Iterator[_T]:
        if self:
            yield self._value                                     # type: ignore

    def __repr__(self) -> str:
        if self:
            return 'MB(' + repr(self._value) + ')'
        else:
            return 'MB()'

    def __bool__(self) -> bool:
        return self._value is not Nothing()

    def __len__(self) -> int:
        if self:
            return 1
        else:
            return 0

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return False
        return self._value == other._value

    def get(self, alt: _T|Nothing=Nothing()) -> _T:
        """Get contents if they exist

        * otherwise return an alternate value of type _T
        * raises ValueError if alternate value needed but not provided

        """
        if self:
            return self._value                                    # type: ignore
        else:
            if alt is Nothing():
                raise ValueError('Alternate return type needed but not provided.')
            else:
                return alt                                        # type: ignore

    def map(self, f: Callable[[_T], _S|Nothing]) -> MB[_S]:
        """Map MB function f over the 0 or 1 elements of this data structure."""
        if self:
            return MB(f(self._value))                             # type: ignore
        else:
            return MB()

    def flatmap(self, f: Callable[[_T], MB[_S]]) -> MB[_S]:
        """Map MB with function f and flatten."""
        if self:
            return f(self._value)                                 # type: ignore
        else:
            return MB()

class XOR(Generic[_L, _R]):
    """Class that either contains a "left" value or "right" value, but not both.

    * implements a left biased Either Monad
    * semantically containing 1 of 2 possible types of values
    * XOR(left: _L, right: _R) produces "left" value
    * XOR(None, right: _R) produces a "right" value
    * therefore None as a value, not implementation detail, can't be put into a "left"
    * in a Boolean context, returns True if a "left", False if a "right"
    * immutable, an XOR does not change after being created
    * immutable semantics, map & flatMap never mutate self

    """
    __slots__ = '_left', '_right'

    def __init__(self, potential_left: _L|Nothing, default_right: _R):
        self._left, self._right = potential_left, default_right

    def __bool__(self) -> bool:
        """Predicate to determine if the XOR contains a "left" or a "right".

        * true if the XOR is a "left"
        * false if the XOR is a "right"
        """
        return self._left is not Nothing()

    def __iter__(self) -> Iterator[_L]:
        """Yields its value if the XOR is a "left"."""
        if self._left is not Nothing():
            yield self._left                                      # type: ignore

    def __repr__(self) -> str:
        return 'XOR(' + repr(self._left) + ', ' + repr(self._right) + ')'

    def __str__(self) -> str:
        if self:
            return '< ' + str(self._left) + ' | >'
        else:
            return '< | ' + str(self._right) + ' >'


    def __len__(self) -> int:
        """Semantically, an XOR always contains just one value."""
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

    def get(self, alt: _L|Nothing=Nothing()) -> _L:
        """Get value if a Left.

        * if the XOR is a left, return its value
        * otherwise, return alt if it is provided
        * raises ValueError if alternate value needed but not provided

        """
        if self._left is Nothing():
            if alt is Nothing():
                raise ValueError('Alternate return type needed but not provided.')
            else:
                return alt                                        # type: ignore
        else:
            return self._left                                     # type: ignore

    def getRight(self, alt: _R|Nothing=Nothing()) -> _R:
        """Get value if a Right.

        * if XOR is a right, return its value
        * otherwise return an alternate value of type _R
        * raises ValueError if alternate value needed but not provided

        """
        if self._left is Nothing():
            return self._right
        else:
            if alt is Nothing():
                raise ValueError('Alternate return type needed but not provided.')
            else:
                return alt                                        # type: ignore

    def getDefaultRight(self) -> _R:
        """Get value if a "right" or the default "right" value.

        * if XOR is a right, return its value
        * otherwise return the left's default right value

        """
        return self._right

    def map(self, f: Callable[[_L], _S|Nothing], right: _R|Nothing=Nothing()) -> XOR[_S, _R]:
        """Map over an XOR.

        * if a "left" apply f and return a "left" if f successful
        * otherwise, if f unsuccessful, return right if not Bottom
        * otherwise, if right Bottom, return the default right value
        * if a "right" return a  "right" with non-bottom right
        * otherwise, if right is bottom, propagate the "right"

        """
        nothing = Nothing()
        if self._left is nothing:
            if right is nothing:
                return XOR(nothing, self._right)
            else:
                return XOR(nothing, right)                        # type: ignore
        else:
            if right is nothing:
                return XOR(f(self._left), self._right)            # type: ignore
            else:
                return XOR(f(self._left), right)                  # type: ignore

    def mapRight(self, g: Callable[[_R], _R]) -> XOR[_L, _R]:
        """Map over a "right" value."""
        if self._left is Nothing():
            return XOR(Nothing(), g(self._right))
        return self

    def flatMap(self, f: Callable[[_L], XOR[_S, _R]]) -> XOR[_S, _R]:
        """Map and flatten a Left value, propagate Right values."""
        if self._left is Nothing():
            return XOR(Nothing(), self._right)
        else:
            return f(self._left)                                  # type: ignore

# Conversion functions

def mb_to_xor(m: MB[_T], right: _R) -> XOR[_T, _R]:
    """Convert a MB to an XOR."""
    if m:
        return XOR(m.get(), right)
    else:
        return XOR(Nothing(), right)

def xor_to_mb(e: XOR[_T,_S]) -> MB[_T]:
    """Convert an XOR to a MB."""
    if e:
        return MB(e.get())
    else:
        return MB()
