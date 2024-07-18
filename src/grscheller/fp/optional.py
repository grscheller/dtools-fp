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

__all__ = [ 'Opt' ]
__author__ = "Geoffrey R. Scheller"
__copyright__ = "Copyright (c) 2023-2024 Geoffrey R. Scheller"
__license__ = "Apache License 2.0"

from typing import Any, Callable, Generic, Iterator, Optional, TypeVar

_T = TypeVar('_T')
_S = TypeVar('_S')
_V = TypeVar('_V')

class Opt(Generic[_T]):
    """Class representing a value of type _T or None

    * _T|None is a poor man's Optional/Maybe Monad built into Python
    * None makes a lousy bottom type since it has almost no methods
    * one must always manually check if a value is None or not
    * aside: () would make a much better bottom, it is at least iterable
    * Opt is my partially successful attempt to give Python a bottom type
    * Opt wraps a _T|None and supplies many useful mostly delegated methods
    * methods get, map, flatMap not delegated
    * use map_, flatmap_ if calling these methods on the contained _T
    * Opt[NoneType] by design is unrepresentable

    """
    __slots__ = '_value',

    def __init__(self, value: Optional[_T]=None):
        self._value = value

    def __iter__(self) -> Iterator[Optional[_T]]:
        yield self._value

    def __bool__(self) -> bool:
        if self._value is None:
            return False
        else:
            return bool(self._value)

    def __repr__(self) -> str:
        if self._value is None:
            return 'Opt()'
        else:
            return 'Opt(' + repr(self._value) + ')'

    def __str__(self) -> str:
        if self._value is None:
            return 'None'
        else:
            return str(self._value)

    def __len__(self) -> int:
        if self._value is None:
            return 0
        else:
            if hasattr(self._value, '__len__'):
                return len(self._value)
            else:
                raise ValueError('Contained object does not len().')

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return False
        return self._value == other._value

    def get(self) -> Optional[_T]:
        """Get contents."""
        return self._value

    def map(self, f: Callable[[_T], _S]) -> Opt[_S]:
        """Map f over the value if not None."""
        if self._value is None:
            return Opt()
        else:
            return Opt(f(self._value))

    def map_(self, f: Callable[[_V], _S]) -> Opt[_S]:
        """Map f over the value if not None.

        * raise ValueError if contained value is not map-able

        """
        if self._value is None:
            return Opt()
        else:
            if hasattr(self._value, 'map'):
                return Opt(f(self._value.map(f)))
            else:
                raise ValueError('Contained object not map-able')

    def flatMap(self, f: Callable[[_T], Opt[_S]]) -> Opt[_S]:
        """Map function f and flatten result."""
        if self._value is None:
            return Opt()
        else:
            return f(self._value)

    def __getitem__(self, index: int) -> Any:
        if self._value is None:
            return None
        else:
            item: Any = None
            try:
                value = self._value
                item = value[index]   # type: ignore
            except IndexError:
                item = None
        return item

    def __setitem__(self, index: int, item: Any) -> None:
        if self._value is None:
            return
        else:
            self._value[index] = item   # type: ignore
        return
