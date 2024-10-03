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

"""### Singleton class representing nothingness

"""
from __future__ import annotations

__all__ = [ '_NoValue', 'noValue' ]

from typing import Final

class _NoValue():
    """#### Singleton class representing a missing value.

    * similar to `None` but while
      * `None` represent "returned no values"
      * `noValue: _NoValue = _NoValue()` represents the absence of a value

    """
    __slots__ = ()

    def __new__(cls) -> _NoValue:
        if not hasattr(cls, 'instance'):
            cls.instance = super(_NoValue, cls).__new__(cls)
        return cls.instance

    def __repr__(self) -> str:
        return 'noValue'

    def __eq__(self, other: object) -> bool:
        if self is other:
            return True
        return False

noValue: Final[_NoValue] = _NoValue()
