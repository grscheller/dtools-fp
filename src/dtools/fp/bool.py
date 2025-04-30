# Copyright 2023-2025 Geoffrey R. Scheller
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


"""
### `_Bool` subclassable boolean

Python (at least CPython for Python 3.13) does not permit bool to be subclassed.

- under-the-hood a bool is just an int
- useful for typing situations (see dtools.fp.err_handling.XOR)
- using the "truthiness" of 1 and "falsiness" of 0
- kept very simple to avoid performance hits, so
  - can be compared with `==` to a boolean
  - neither `_True()` nor `_False()` are singletons (nor pretend singletons)
  - don't use in arithmetic expressions
- using underscore `_` in names to emphasize this construct
  - should be only used as an implementation detail in library code
  - should not be used in application code

"""

from __future__ import annotations

from typing import Final

__all__ = ['_Bool', '_True', '_False', 'TRUE', 'FALSE' ]


class _Bool(int):
    def __new__(cls, val: int = 0) -> _Bool:
        if val == 0:
            return super(_Bool, cls).__new__(cls, 0)
        return super(_Bool, cls).__new__(cls, 1)

    def __bool__(self) -> bool:
        return bool(int(self))

    def __repr__(self) -> str:
        if self:
            return '_True()'
        return '_False()'

    def __str__(self) -> str:
        if self:
            return 'True'
        return 'False'


class _True(_Bool):
    def __new__(cls, val: int = 1) -> _True:
        return super(_Bool, cls).__new__(cls, 1)


class _False(_Bool):
    def __new__(cls, val: int = 0) -> _False:
        return super(_Bool, cls).__new__(cls, 0)


TRUE: Final[_True] = _True()
FALSE: Final[_False] = _False()
