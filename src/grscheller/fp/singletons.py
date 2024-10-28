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

"""### Singleton classes

"""
from __future__ import annotations

__all__ = [ 'NoValue', 'noValue', 'Sentinel', '_sentinel' ]

from typing import Final, final

@final
class NoValue():
    """#### Singleton class representing a missing value.

    * similar to `None` but while
      * `None` represents "returned no values"
      * `noValue: NoValue = NoValue()` represents the absence of a value
    * usage
      * import noValue, only import NoValue if needed for type annotation
        * NoValue made exportable for
          * type annotation
          * documentation purposes
      * compare using `is` and `is not`
        * two non-existing values should not be comparable as equal
          * `None` means returned no values, so `None == None` makes sense
          * if one or both values are "missing" then what is there to compare?

    """
    __slots__ = ()
    _instance = None

    def __new__(cls) -> NoValue:
        if cls._instance is None:
            cls._instance = super(NoValue, cls).__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        return

    def __repr__(self) -> str:
        return 'noValue'

    def __eq__(self, other: object) -> bool:
        return False

noValue: Final[NoValue] = NoValue()

@final
class Sentinel():
    """#### Singleton class representing a sentinel value.

    * intended for library code, not application code
    * useful substitute for `None` as a hidden sentinel value
      * allows `None` to be stored in data structures
      * allows end users to use `None` for a sentinel value
      * allows equals itself (unlike `noValue`)
    * usage
      * import both _sentinel & Sentinel into library code
        * use just _sentinel if you can get away with it
        * Sentinel exported
          * to be used with type annotations
          * for documentation purposes
          * so eval(repr(_sentinel)) works as expected

    """
    __slots__ = ()
    _instance = None

    def __new__(cls) -> Sentinel:
        if cls._instance is None:
            cls._instance = super(Sentinel, cls).__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        return

    def __repr__(self) -> str:
        return 'Sentinel()'

    def __eq__(self, other: object) -> bool:
        if self is other:
            return True
        return False

_sentinel: Final[Sentinel] = Sentinel()
"""The singleton object produced by the Sentinel class.

The original idea was to keep the constructor "private" and hand around this
copy. Found that the Final annotation was not protecting _sentinel from being
reassigned to some other random object.

Found that just using Sentinel() itself accomplished what I wanted.
"""

