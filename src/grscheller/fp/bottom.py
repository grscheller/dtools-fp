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

"""A partially successful attempt to give Python a "bottom" type.

_T|None acts like a poor man's Optional/Maybe Monad but None is a lousy bottom

* semantically a singleton, it can still be instantiated
* it really is not a subtype of all types, has almost no methods
* () would make a much better bottom, it is at least iterable
* a value must manually be checked whether it is None or not

Class Opt implements the Maybe monad with Opt() acting like a bottom, at least
for Opt[_T].

* delegates most standard functions/methods to the contained object, if it exists
* get_, map_, flatMap_ and some inherited from object act on the Opt container
* use map_(lambda x: x.foobar()) to access specific methods of the underlying object
* Opt() not a singleton, so use == and != instead of "is" or "is not"
* Opt[NoneType] by design is unrepresentable

The project maintainer realized with a little effort, he could make Opt() behave
like a bottom type. It is really only a bottom type for Opt[_T], it can be
instantiated, and then not a singleton, but we can pretend.

"""

from __future__ import annotations

__all__ = [ 'Opt' ]
__author__ = "Geoffrey R. Scheller"
__copyright__ = "Copyright (c) 2023-2024 Geoffrey R. Scheller"
__license__ = "Apache License 2.0"

from typing import Any, Callable, Generic, Iterator, Optional, TypeVar

_T = TypeVar('_T')
_S = TypeVar('_S')
_V = TypeVar('_V')
_U = TypeVar('_U')

class Opt(Generic[_T]):
    """Implements an Optional/Maybe Monad with a "bottom value" Opt().

    * semantically represents a value of type _T|None
    * delegates most standard functions/methods to the contained object, if it exists
    * get_, map_, flatMap_ and some inherited from object act on the Opt container
    * use map_(lambda x: x.foobar()) to access specific methods of contained object
    * use map to map over the underlying object
    * Opt() is a better "bottom" value than either None or ()
    * Opt() not a singleton, so use == and != instead of "is" and "is not"
    * Opt[NoneType] by design is unrepresentable

    """
    __slots__ = '_value',

    def __init__(self, value: Optional[_T]=None):
        self._value = value

    def __iter__(self) -> Iterator[Optional[_T]]:
        if self._value is not None:
            yield self._value

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

    def __bool__(self) -> bool:
        if self._value is None:
            return False
        else:
            return bool(self._value)

    def __len__(self) -> int:
        if self._value is None:
            return 0
        else:
            if hasattr(self._value, '__len__'):
                return len(self._value)
            else:
                msg = f'contained object of type {type(self._value)} '
                msg += 'does not have a length.'
                raise TypeError(msg)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return False
        return self._value == other._value

    def get_(self, alt: Optional[_T]=None) -> _T:
        """Get contents if they exist

        * otherwise return an alternate value of type _T
        * raises ValueError if alternate value needed but not provided

        """
        if self._value is None:
            if alt is None:
                raise ValueError('Alternate return type needed but not provided.')
            else:
                return alt
        else:
            return self._value

    def map(self, f: Callable[[_V], _S]) -> Opt[_S]:
        """Map f over the value if not None.

        * raise TypeError if contained value is not map-able

        """
        if self._value is None:
            return Opt()
        else:
            if hasattr(self._value, 'map'):
                return Opt(self._value.map(f))
            else:
                raise TypeError('Contained object not map-able')

    def map_(self, f: Callable[[_T], _S]) -> Opt[_S]:
        """Map f over the Opt container, not its value."""
        if self._value is None:
            return Opt()
        else:
            return Opt(f(self._value))

    def flatMap(self, f: Callable[[_U], _V]) -> Opt[_V]:
        """flatMap f over the value if not None."""
        if self._value is None:
            return Opt()
        else:
            if hasattr(self._value, 'flatMap'):
                return Opt(self._value.flatMap(f))
            else:
                raise TypeError('Contained value is not bind-able.')

    def flatMap_(self, f: Callable[[_T], Opt[_S]]) -> Opt[_S]:
        """flatMap function f over Opt container, not its value."""
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
