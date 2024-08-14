# Copyright 2024 Geoffrey R. Scheller
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

"""### Attempt to give Python a "bottom" type

* `nada` is a singleton
  * while a true bottom type has no instances
  * Python's evolving typing system seems to reject the concept
* types like `None` and `()` make for lousy bottoms
  * note that `~T|None` and `~T|()` are a poor man's Maybe Monads
    * `None` has no length and is not indexable
    *  `()` is at least iterable
    * both take few methods (much less EVERY method)
      * both must be constantly checked for
        * preventing one from blissfully go down the "happy path"
"""

from __future__ import annotations
from typing import Callable, cast, Generic, Final, Iterator, TypeVar

__all__ = ['nada', 'Nada']

_Sentinel = tuple[None, tuple[None, tuple[None, tuple[()]]]]
_s: Final[_Sentinel] = None, (None, (None, ()))

U = TypeVar('U')
V = TypeVar('V')

class Nada():
    """
    #### Singleton semantically represents a missing value.

    * singleton nada: Nada = Nada() represents a non-existent value
    * makes for a better "bottom type" than either `None` or `()`
        * returns itself for arbitrary method calls
        * returns itself if called as a Callable with arbitrary arguments
        * interpreted as an empty container by standard Python functions
        * comparison ops compare true only when 2 non-missing values compare true
          * when compared to itself behaves somewhat like IEEE Float NAN's
            * `nada is nada` is true
            * `nada == nada` is false
            * `nada != nada` is true
    """
    __slots__ = ()

    def __new__(cls) -> Nada:
        if not hasattr(cls, 'instance'):
            cls.instance = super(Nada, cls).__new__(cls)
        return cls.instance

