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

"""#### An attempt to give Python a "bottom" type

While a true bottom type has no instances, `nada` is a singleton. Python's
evolving typing system seems to reject the concept of a true bottom type.

   * types like `None` and `()` make for lousy bottoms
     * they take few methods (much less EVERY method)
     * `None` has no length and not indexable, `()` is at least iterable
     * returned values must be constantly checked for
       * preventing one from blissfully go down the "happy path"
     * `None` and `()` are commonly used as sentinel values
       * hindering both as being interpreted as "nothingness"

The `nada` object makes for a better bottom like singleton
object than either `None` and `()` do."""

from __future__ import annotations
from typing import Any, Callable, Final, Iterator, NewType

__all__ = ['nada', 'Nada']

_S = NewType('_S', tuple[None, tuple[None, tuple[None, tuple[()]]]])
_sentinel: Final[_S] = _S((None, (None, (None, ()))))

class Nada():
    """
    #### Singleton semantically represents a missing value.

    * singleton nada: Nada = Nada() represents a non-existent value
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
            cls._hash = hash((_sentinel, (_sentinel,)))
        return cls.instance

    def __iter__(self) -> Iterator[Any]:
        return iter(())

    def __hash__(self) -> int:
        return self._hash

    def __repr__(self) -> str:
        return 'nada'

    def __bool__(self) -> bool:
        return False

    def __len__(self) -> int:
        return 0

    def __add__(self, right: Any) -> Nada:
        return Nada()

    def __radd__(self, left: Any) -> Nada:
        return Nada()

    def __mul__(self, right: Any) -> Nada:
        return Nada()

    def __rmul__(self, left: Any) -> Nada:
        return Nada()

    def __eq__(self, right: Any) -> bool:
        """Never equals anything, even itself."""
        return False

    def __ne__(self, right: Any) -> bool:
        """Always does not equal anything, even itself."""
        return True

    def __ge__(self, right: Any) -> bool:
        return False

    def __gt__(self, right: Any) -> bool:
        return False

    def __le__(self, right: Any) -> bool:
        return False

    def __lt__(self, right: Any) -> bool:
        return False

    def __getitem__(self, index: int|slice) -> Any:
        return Nada()

    def __setitem__(self, index: int|slice, item: Any) -> None:
        return

    def __call__(*args: Any, **kwargs: Any) -> Any:
        return Nada()

    def __getattr__(self, name: str) -> Callable[[Any], Any]:
        """Comment out for doc generation, pdoc gags on this method."""
        def method(*args: Any, **kwargs: Any) -> Any:
            return Nada()
        return method

    def get(self, alt: Any=_sentinel) -> Any:
        """
        ##### Get an alternate value, defaults to Nada().
        """
        if alt == _sentinel:
            return Nada()
        else:
            return alt

nada = Nada()
