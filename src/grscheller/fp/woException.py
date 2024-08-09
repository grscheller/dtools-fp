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
from grscheller.untyped.nothing import Nothing, nothing

T = TypeVar('T')
S = TypeVar('S')
L = TypeVar('L')
R = TypeVar('R')

class MB(Generic[T]):
    """Class representing a potentially missing value.

    * where MB(value) contains a possible value of type ~T
    * MB( ) semantically represent a "Nothing"
    * implementation wise MB( ) contains a nothing: Nothing
    * therefore nothing = Nothing(), as a value, cannot be put into a MB
    * immutable, a MB does not change after being created
    * immutable semantics, map and flatMap produce new instances

    """
    __slots__ = '_value',

    def __init__(self, value: T|Nothing=nothing) -> None:
        self._value = value

    def __bool__(self) -> bool:
        return not self._value is nothing

    def __iter__(self) -> Iterator[T]:
        if self:
            yield self._value

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
        return self._value == other._value

    def get(self, alt: T|Nothing=Nothing()) -> T:
        """Get non-existent contents

        * if given, return an alternate value of type ~T
        * otherwise, raises `ValueError`
        * get will return nothing = Nothing()
        * it will happily return `None` or `()`

        """
        if self:
            return self._value
        else:
            if alt is Nothing():
                raise ValueError('Alternate return type not provided.')
            else:
                return alt

    def map(self, f: Callable[[T], S|Nothing]) -> MB[S]:
        """Map MB function f over the 0 elements of this data structure."""
        return (MB(f(self._value)) if self else MB())

    def flatmap(self, f: Callable[[T], MB[S]]) -> MB[S]:
        """Map MB with function f and flatten."""
        return (f(self._value) if self else MB())

class XOR(Generic[L, R]):
    """Class that either contains a "left" value or "right" value, but not both.

    * implements a left biased Either Monad
    * semantically containing 1 of 2 possible types of values
    * XOR(left: ~L, right: ~R) produces "left" value
    * XOR(nothing, right: ~R) produces a "right" value
    * therefore nothing: Nothing as a value cannot be stored as a "left"
    * in a Boolean context, returns True if a "left", False if a "right"
    * immutable, an XOR does not change after being created
    * immutable semantics, map & flatMap return new instances

    """
    __slots__ = '_left', '_right'

    def __init__(self, potential_left: L|Nothing, default_right: R):
        self._left, self._right = potential_left, default_right

    def __bool__(self) -> bool:
        """Predicate to determine if the XOR contains a "left" or a "right".

        * true if the XOR is a "left"
        * false if the XOR is a "right"
        """
        return self._left is not Nothing()

    def __iter__(self) -> Iterator[L]:
        """Yields its value if the XOR is a "left"."""
        if self:
            yield self._left

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

    def get(self, alt: L|Nothing=Nothing()) -> L:
        """Get value if a Left.

        * if the XOR is a left, return its value
        * otherwise, return alt if it is provided
        * raises `ValueError` if alternate value needed but not provided

        """
        if self._left is Nothing():
            if alt is Nothing():
                raise ValueError('Alternate return type needed but not provided.')
            else:
                return alt
        else:
            return self._left

    def getRight(self, alt: R|Nothing=Nothing()) -> R:
        """Get value if a Right.

        * if XOR is a right, return its value
        * otherwise return an alternate value of type ~R
        * raises `ValueError` if alternate value needed but not provided

        """
        if not self:
            return self._right
        else:
            if alt is Nothing():
                raise ValueError('Alternate return type needed but not provided.')
            else:
                return alt

    def getDefaultRight(self) -> R:
        """Get value if a "right" or the default "right" value.

        * if XOR is a right, return its value
        * otherwise return the left's default right value

        """
        return self._right

    def map(self, f: Callable[[L], S|Nothing], right: R|Nothing=Nothing()) -> XOR[S, R]:
        """Map over an XOR.

        * if a "Left" XOR map f and return a "Left" XOR if f successful
        * otherwise, if f unsuccessful, return "Right" XOR with right not nothing: Nothing
        * otherwise, if right is nothing, return the default "Right" XOR
        * if a "Right" return a "Right" XOR with a non-nothing right
        * otherwise, if right is nothing, propagate new "Right" XOR instance

        """
        nothing = Nothing()
        if self._left is nothing:
            if right is nothing:
                return XOR(nothing, self._right)
            else:
                return XOR(nothing, right)
        else:
            if right is nothing:
                return XOR(f(self._left), self._right)
            else:
                return XOR(f(self._left), right)

    def mapRight(self, g: Callable[[R], R]) -> XOR[L, R]:
        """Map over a "right" value."""
        if self._left is Nothing():
            return XOR(Nothing(), g(self._right))
        return self

    def flatMap(self, f: Callable[[L], XOR[S, R]]) -> XOR[S, R]:
        """Map and flatten a Left value, propagate Right values."""
        if self._left is Nothing():
            return XOR(Nothing(), self._right)
        else:
            return f(self._left)

# Conversion functions

def mb_to_xor(m: MB[T], right: R) -> XOR[T, R]:
    """Convert a MB to an XOR."""
    if m:
        return XOR(m.get(), right)
    else:
        return XOR(Nothing(), right)

def xor_to_mb(e: XOR[T,S]) -> MB[T]:
    """Convert an XOR to a MB."""
    if e:
        return MB(e.get())
    else:
        return MB()
