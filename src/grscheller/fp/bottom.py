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

"""An attempt to give Python a "bottom" type than either None or ().

* Bottom(): Bottom is a singleton representing the absence of a value
* unlike a true bottom, it can be instantiated
* Bottom() can be used with most standard Python functions
* Bottom() accepts most standard Python methods (still a work in progress)
* _T|None and _T|() can act like a poor man's Optional/Maybe Monad
* both None and () are lousy bottoms
* both don't accept many methods, None has no length, at least () is iterable
* both must constantly be checked for as return values
* many developers use None and () as a sentinel values
* used as sentinels developers like to be able to store them in data structures

"""

from __future__ import annotations

__all__ = [ 'Bottom' ]
__author__ = "Geoffrey R. Scheller"
__copyright__ = "Copyright (c) 2023-2024 Geoffrey R. Scheller"
__license__ = "Apache License 2.0"

from typing import Any, Callable, ClassVar, Generic, Iterator, Optional, TypeVar

_T = TypeVar('_T')
_S = TypeVar('_S')

class Bottom():
    """Attempt to give Python a "bottom" type.

    * semantically represents an empty container containing Any type
    * delegates most standard functions/methods to the contained object, if it exists
    * use map_(lambda x: x.foobar()) to access specific methods of contained object
    * use map to map over the underlying object
    * Implemented with the Singleton Pattern

    """
    __slots__ = '_bottom',

    def __new__(cls) -> Bottom:
        if not hasattr(cls, 'instance'):
            cls.instance = super(Bottom, cls).__new__(cls)
        return cls.instance

    def __init__(self) -> None:
        self._bottom = ()

    def __iter__(self) -> Iterator[Any]:
        return iter(self._bottom)

    def __repr__(self) -> str:
        return 'Bottom()'

    def __str__(self) -> str:
        return 'bottom'

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

    def map(self, f: Callable[[_T], _S]) -> Bottom:
        """Semantically map function f over an empty container."""
        return Bottom()

    def flatMap(self, f: Callable[[_T], _S]) -> Bottom:
        """Semantically flatMap function f over an empty container."""
        return Bottom()

    def __getitem__(self, index: int) -> Bottom:
        return Bottom()

    def __setitem__(self, index: int, item: Any) -> None:
        return
