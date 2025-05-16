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


"""Class `Bool` - Subclassable Boolean

Python does not permit bool to be subclassed, but `int` can be subclassed.
Under-the-hood a `bool` is just an `int`. Though it would be possible to
make Truth() and Lie() singletons, I did not want to take the performance
hit to enforce this.
"""

from __future__ import annotations

from typing import Final

__all__ = ['Bool', 'Truth', 'Lie', 'TRUTH', 'LIE' ]


class Bool(int):
    """Subclassable Boolean-like class.

    - best practices
      - compared with `==` or `!=` not `is` or `not is`
      - only use Bool as a type, not as a constructor 
      - when using Python shortcut logic remember
        - the `not` statement convert a Bool to a bool
          - `TRUTH` is truthy, `LIE` is falsy
            - an instance of `Truth` is truthy
            - an instance of `Lie` is falsy
        - shortcut logic is lazy
          - the last truthy thing evaluated is returned
          - and it is not converted to a bool
    """
    def __new__(cls) -> Bool:
        return super(Bool, cls).__new__(cls, 0)

    def __repr__(self) -> str:
        if self:
            return 'Truth()'
        return '_Lie()'


class Truth(Bool):
    """Truthy Bool subclass - not a singleton."""
    def __new__(cls) -> Truth:
        return super(Bool, cls).__new__(cls, 1)


class Lie(Bool):
    """Falsy Bool subclass - not a singleton."""
    def __new__(cls) -> Lie:
        return super(Bool, cls).__new__(cls, 0)


TRUTH: Final[Truth] = Truth()
LIE: Final[Lie] = Lie()
