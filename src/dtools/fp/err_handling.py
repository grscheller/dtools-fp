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

"""### Module dtools.fp.err_handling - monadic error handling

Functional data types to use in lieu of exceptions.

- *class* MB: maybe (optional) monad
- *class* XOR: left biased either monad

"""

from __future__ import annotations

__all__ = ['MB', 'XOR', 'LEFT', 'RIGHT']

from collections.abc import Callable, Iterable, Iterator, Sequence
from typing import cast, Final, Never, overload, TypeVar
from .bool import _Bool as Both, _True as Left, _False as Right
from .singletons import Sentinel


# -- class MB ------------------------------------------------------------------

D = TypeVar('D')


class MB[D]:
    """Maybe monad - class wrapping a potentially missing value.

    - where `MB(value)` contains a possible value of type `~D`
    - `MB()` semantically represent a non-existent or missing value of type `~D`
    - immutable semantics, map & bind return new instances
      - can store any value of any type with one exception
        - if `~D` is `Sentinel`, storing `Sentinel(MB)` results in a MB()
      - warning: hashability invalidated if contained value is mutated
      - warning: hashed values invalidated if `put` or `pop` methods called
    - unsafe methods `get` and `pop`
      - could raise `ValueError` if MB is empty and alt values not given
    - stateful methods `put` and `pop`
      - useful to treat a `MB` as a stateful object
      - basically a container that can contain 1 or 0 objects

    """

    __slots__ = ('_value',)
    __match_args__ = ('_value',)

    T = TypeVar('T')
    U = TypeVar('U')
    V = TypeVar('V')

    @overload
    def __init__(self) -> None: ...
    @overload
    def __init__(self, value: D) -> None: ...

    def __init__(self, value: D | Sentinel = Sentinel('MB')) -> None:
        self._value: D | Sentinel = value

    def __bool__(self) -> bool:
        return self._value is not Sentinel('MB')

    def __iter__(self) -> Iterator[D]:
        if self:
            yield cast(D, self._value)

    def __repr__(self) -> str:
        if self:
            return 'MB(' + repr(self._value) + ')'
        return 'MB()'

    def __len__(self) -> int:
        return 1 if self else 0

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return False

        if self._value is other._value:
            return True
        if self._value == other._value:
            return True
        return False

    @overload
    def get(self) -> D | Never: ...
    @overload
    def get(self, alt: D) -> D: ...
    @overload
    def get(self, alt: Sentinel) -> D | Never: ...

    def get(self, alt: D | Sentinel = Sentinel('MB')) -> D | Never:
        """Return the contained value if it exists, otherwise an alternate value.

        - alternate value must be of type `~D`
        - raises `ValueError` if an alternate value is not provided but needed

        """
        _sentinel: Final[Sentinel] = Sentinel('MB')
        if self._value is not _sentinel:
            return cast(D, self._value)
        if alt is _sentinel:
            msg = 'MB: an alternate return type not provided'
            raise ValueError(msg)
        return cast(D, alt)

    def put(self, value: D) -> None:
        """Put a value in the MB if empty, if not empty do nothing.

        - warning: method will invalidate hashability if used

        """
        if self._value is Sentinel('MB'):
            self._value = value

    def pop(self) -> D | Never:
        """Pop the value if the MB is not empty, otherwise fail.

        - warning: method will invalidate hashability if used

        """
        _sentinel: Final[Sentinel] = Sentinel('MB')
        if self._value is _sentinel:
            msg = 'MB: Popping from an empty MB'
            raise ValueError(msg)
        popped = cast(D, self._value)
        self._value = _sentinel
        return popped

    def map[U](self, f: Callable[[D], U]) -> MB[U]:
        """Map function `f` over contents.

        - if `f` should fail, return a MB()

        """
        if self._value is Sentinel('MB'):
            return cast(MB[U], self)
        try:
            return MB(f(cast(D, self._value)))
        except RuntimeError:
            return MB()

    def bind[U](self, f: Callable[[D], MB[U]]) -> MB[U]:
        """Map `MB` with function `f` and flatten."""
        try:
            return f(cast(D, self._value)) if self else MB()
        except RuntimeError:
            return MB()

    @staticmethod
    def call[U, V](f: Callable[[U], V], u: U) -> MB[V]:
        """Return MB wrapped result of a function call that can fail"""
        try:
            return MB(f(u))
        except RuntimeError:
            return MB()

    @staticmethod
    def lz_call[U, V](f: Callable[[U], V], u: U) -> Callable[[], MB[V]]:
        """Return a MB of a delayed evaluation of a function"""

        def ret() -> MB[V]:
            return MB.call(f, u)

        return ret

    @staticmethod
    def idx[V](v: Sequence[V], ii: int) -> MB[V]:
        """Return a MB of an indexed value that can fail"""
        try:
            return MB(v[ii])
        except IndexError:
            return MB()

    @staticmethod
    def lz_idx[V](v: Sequence[V], ii: int) -> Callable[[], MB[V]]:
        """Return a MB of a delayed indexing of a sequenced type that can fail"""

        def ret() -> MB[V]:
            return MB.idx(v, ii)

        return ret

    @staticmethod
    def sequence[T](itab_mb_d: Iterable[MB[T]]) -> MB[Iterator[T]]:
        """Sequence an indexable of type `MB[~T]`

        * if the iterated `MB` values are not all empty,
          * return a `MB` of an iterator of the contained values
          * otherwise return an empty `MB`

        """
        item: list[T] = []

        for mb_d in itab_mb_d:
            if mb_d:
                item.append(mb_d.get())
            else:
                return MB()

        return MB(iter(item))


# -- class XOR -----------------------------------------------------------------

L = TypeVar('L')
R = TypeVar('R')

LEFT = Left()
RIGHT = Right()


class XOR[L, R]:
    """Either monad - class semantically containing either a left or a right
    value, but not both.

    - implements a left biased Either Monad
      - `XOR(value: ~L)` or `XOR(value: ~L, LEFT)` produces a left `XOR`
      - `XOR(value: ~L, RIGHT)` produces a right `XOR`
    - in a Boolean context
      - `True` if a left `XOR`
      - `False` if a right `XOR`
    - two `XOR` objects compare as equal when
      - both are left values or both are right values whose values
        - are the same object
        - compare as equal
    - immutable, an `XOR` does not change after being created
      - immutable semantics, map & bind return new instances
        - warning: contained value need not be immutable
        - warning: not hashable if value is mutable

    """

    __slots__ = '_value', '_side'
    __match_args__ = ('_value', '_side')

    T = TypeVar('T')
    U = TypeVar('U')
    V = TypeVar('V')
    E = TypeVar('E')

    @overload
    def __new__(cls, value: L) -> XOR[L, R]: ...
    @overload
    def __new__(cls, value: L, side: Right) -> XOR[L, R]: ...
    @overload
    def __new__(cls, value: R, side: Left) -> XOR[L, R]: ...

    def __new__(cls, value: L | R, side: Both = RIGHT) -> XOR[L, R]:
        return super(XOR, cls).__new__(cls)

    @overload
    def __init__(self, value: L) -> None: ...
    @overload
    def __init__(self, value: L, side: Left) -> None: ...
    @overload
    def __init__(self, value: R, side: Right) -> None: ...

    def __init__(self, value: L | R, side: Both = LEFT) -> None:
        self._value = value
        self._side = side

    def __bool__(self) -> bool:
        return self._side == LEFT

    def __iter__(self) -> Iterator[L]:
        if self:
            yield cast(L, self._value)

    def __repr__(self) -> str:
        if self:
            return 'XOR(' + repr(self._value) + ', LEFT)'
        return 'XOR(' + repr(self._value) + ', RIGHT)'

    def __str__(self) -> str:
        if self:
            return '< ' + str(self._value) + ' | >'
        return '< | ' + str(self._value) + ' >'

    def __len__(self) -> int:
        # An XOR always contains just one value.
        return 1

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return False

        if self and other:
            if (self._value is other._value) or (self._value == other._value):
                return True

        if not self and not other:
            if (self._value is other._value) or (self._value == other._value):
                return True

        return False

    def get(self) -> L | Never:
        """Get value if a left. Unsafe convenience function.

        - if the `XOR` is a "left" XOR
          - return its value
        - if the `XOR` contains a right value
          - raises `ValueError`
          - best practice is to first check the `XOR` in a boolean context

        """
        if self._side == RIGHT:
            msg = 'XOR: get method called on a right valued XOR'
            raise ValueError(msg)
        return cast(L, self._value)

    def get_left(self) -> MB[L]:
        """Get value of `XOR` if a left. Safer version of `get` method.

        - if `XOR` contains a left value, return it wrapped in a MB
        - if `XOR` contains a tight value, return MB()

        """
        if self._side == LEFT:
            return MB(cast(L, self._value))
        return MB()

    def get_right(self) -> MB[R]:
        """Get value of `XOR` if a right

        - if `XOR` contains a right value, return it wrapped in a MB
        - if `XOR` contains a left value, return MB()

        """
        if self._side == RIGHT:
            return MB(cast(R, self._value))
        return MB()

    def map[U](self, f: Callable[[L], U], fail: R) -> XOR[U, R]:
        """Map over if a left value.

        - if `XOR` is a left then map `f` over its value
          - if `f` successful return a left `XOR[U, R]`
          - if `f` unsuccessful return right `XOR[S, R]`
            - swallows any exceptions `f` may throw
        - if `XOR` is a right
          - return new `XOR(right=self._right): XOR[S, R]`
          - use method `map_right` to adjust the returned value

        """
        if self._side == RIGHT:
            return cast(XOR[U, R], self)
        try:
            applied = f(cast(L, self._value))
        except RuntimeError:
            return cast(XOR[U, R], XOR(fail, side=RIGHT))

        return XOR(applied)

    def map_right(self, g: Callable[[R], R], alt_right: R) -> XOR[L, R]:
        """Map over a right value."""
        if self._side == LEFT:
            return self

        try:
            value = g(cast(R, self._value))
        except RuntimeError:
            value = alt_right

        return XOR(value, RIGHT)

    def change_right[V](self, right: V) -> XOR[L, V]:
        """Change a right value's type and value."""
        if self._side == LEFT:
            return cast(XOR[L, V], self)

        return XOR[L, V](right, RIGHT)

    def bind[U](self, f: Callable[[L], XOR[U, R]], alt_right: R) -> XOR[U, R]:
        """Flatmap over the left value

        - map over and then trivially "flatten" the left value
        - propagate right values
        - if bind fails, return alt_right wrapped in an right XOR
          - WARNING: swallows RuntimeErrors

        """
        if self:
            try:
                return f(cast(L, self._value))
            except RuntimeError:
                return XOR(alt_right, RIGHT)

        return cast(XOR[U, R], self)

    @staticmethod
    def call[U, V](f: Callable[[U], V], left: U) -> XOR[V, RuntimeError]:
        """Return XOR wrapped result of a function call that can fail"""
        try:
            xor = XOR[V, RuntimeError](f(left), LEFT)
        except RuntimeError as exc:
            xor = XOR(exc, side=RIGHT)

        return xor

    @staticmethod
    def lz_call[U, V](
        f: Callable[[U], V], arg: U
    ) -> Callable[[], XOR[V, RuntimeError]]:
        """Return an XOR of a delayed evaluation of a function"""

        def ret() -> XOR[V, RuntimeError]:
            return XOR.call(f, arg)

        return ret

    @staticmethod
    def idx[V](v: Sequence[V], ii: int) -> XOR[V, IndexError]:
        """Return an XOR of an indexed value that can fail"""
        try:
            xor = XOR[V, IndexError](v[ii], LEFT)
        except IndexError as exc:
            xor = XOR(exc, side=RIGHT)

        return xor

    @staticmethod
    def lz_idx[V](v: Sequence[V], ii: int) -> Callable[[int], XOR[V, IndexError]]:
        """Return an XOR of a delayed indexing of a sequenced type that can fail"""

        def ret(ii: int) -> XOR[V, IndexError]:
            return XOR.idx(v, ii)

        return ret

    @staticmethod
    def sequence(itab_xor_lr: Iterable[XOR[L, R]], right: R) -> XOR[Iterator[L], R]:
        """Sequence an indexable of type `XOR[~L, ~R]`

        - if the iterated `XOR` values are all lefts, then
          - return an `XOR` of an iterable of the left values
        - otherwise return a right XOR containing the first right encountered

        """
        ts: list[L] = []

        for xor_lr in itab_xor_lr:
            if xor_lr:
                ts.append(xor_lr.get())
            else:
                return XOR(right, RIGHT)

        return XOR(iter(ts))
