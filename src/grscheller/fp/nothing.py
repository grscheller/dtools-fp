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

"""A nothing is an attempt to give Python a "bottom" type.

* nothing: Nothing = Nothing(): is a singleton representing an absent value
* unlike a true bottom, it can be instantiated
* Nothing() can be used with most standard Python functions
* Nothing() accepts most standard Python methods (still a work in progress)
* types _T|None and _T|() both can act like a poor man's Optional/Maybe Monad
* both None and () are lousy bottoms
* both don't accept many methods, None has no length, at least () is iterable
* both must constantly be checked for in return values
* many developers use None and () as sentinel values
* as sentinels Null & () should be capable of being stored as values

"""

from __future__ import annotations

__all__ = [ 'Nothing', 'nothing' ]
__author__ = "Geoffrey R. Scheller"
__copyright__ = "Copyright (c) 2023-2024 Geoffrey R. Scheller"
__license__ = "Apache License 2.0"

from typing import Any, Callable, ClassVar, Generic, Iterator, Optional, TypeVar

_T = TypeVar('_T')
_S = TypeVar('_S')

class Nothing():
    """Attempt to give Python a "bottom" type.

    * semantically represents an empty container containing Any type
    * delegates most standard functions/methods to the contained object, if it exists
    * use map_(lambda x: x.foobar()) to access specific methods of contained object
    * use map to map over the underlying object
    * Implemented with the Singleton Pattern

    """
    __slots__ = '_bottom',

    def __new__(cls) -> Nothing:
        if not hasattr(cls, 'instance'):
            cls.instance = super(Nothing, cls).__new__(cls)
        return cls.instance

    def __init__(self) -> None:
        self._bottom = ()

    def __iter__(self) -> Iterator[Any]:
        return iter(self._bottom)

    def __repr__(self) -> str:
        return 'Nothing()'

    def __str__(self) -> str:
        return 'nothing'

    def __bool__(self) -> bool:
        return False

    def __len__(self) -> int:
        return 0

    def get(self, alt: Optional[_T]=None) -> _T:
        """return a value of type _T

        * raises ValueError if an alternate value is not provided

        """
        if alt is None:
            raise ValueError('Alternate return type needed but not provided.')
        else:
            return alt

    def map(self, f: Callable[[_T], _S]) -> Nothing:
        """Semantically map function f over an empty container."""
        return Nothing()

    def flatMap(self, f: Callable[[_T], _S]) -> Nothing:
        """Semantically flatMap function f over an empty container."""
        return Nothing()

    def __getitem__(self, index: int) -> Nothing:
        return Nothing()

    def __setitem__(self, index: int, item: Any) -> None:
        return

nothing = Nothing()
