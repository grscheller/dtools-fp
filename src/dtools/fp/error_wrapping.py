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

"""### Module dtools.fp.error_wrapping - monadic error handling

Functional data types to use in lieu of exceptions.

- *class* MayBe2: maybe (optional) monad
- *class* Xor2: left biased either monad

"""

from __future__ import annotations

__all__ = ['MayBe2', 'Xor2', 'LEFT2', 'RIGHT2']

from collections.abc import Callable, Iterable, Iterator, Sequence
from typing import cast, Final, Never, overload, TypeVar
from .bool import _Bool as Both, _True as Left, _False as Right
from .singletons import Sentinel


# -- class MayBe2 ------------------------------------------------------------------

D = TypeVar('D', covariant=True)


class MayBe2[D]:
    """Maybe monad - class wrapping a potentially missing value.

    - where `MayBe2(value)` contains a possible value of type `~D`
    - `MayBe2()` semantically represent a non-existent or missing value of type `~D`
    - immutable semantics
      - immutable, therefore made covariant
      - can store any value of any type with one exception
        - if `~D` is `Sentinel`, storing `Sentinel(MayBe2)` results in a MayBe2()
    - WARNING: hashability invalidated if contained value is not hashable
      - hash function will fail if `MayBe2` contains an unhashable value
    - WARNING: unsafe method `get`
      - will raise `ValueError` if MayBe2 empty and an alt return value not given
      - best practice is to first check the MayBe2 in a boolean context

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

    def __init__(self, value: D | Sentinel = Sentinel('MayBe2')) -> None:
        self._value: D | Sentinel = value

    def __hash__(self) -> int:
        return hash((Sentinel('MayBe2'), self._value))

    def __bool__(self) -> bool:
        return self._value is not Sentinel('MayBe2')

    def __iter__(self) -> Iterator[D]:
        if self:
            yield cast(D, self._value)

    def __repr__(self) -> str:
        if self:
            return 'MayBe2(' + repr(self._value) + ')'
        return 'MayBe2()'

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

    def get(self, alt: D | Sentinel = Sentinel('MayBe2')) -> D | Never:
        """Return the contained value if it exists, otherwise an alternate value.

        - alternate value must be of type `~D`
        - raises `ValueError` if an alternate value is not provided but needed

        """
        _sentinel: Final[Sentinel] = Sentinel('MayBe2')
        if self._value is not _sentinel:
            return cast(D, self._value)
        if alt is _sentinel:
            msg = 'MayBe2: an alternate return type not provided'
            raise ValueError(msg)
        return cast(D, alt)

    def map[U](self, f: Callable[[D], U]) -> MayBe2[U]:
        """Map function `f` over contents."""

        if self:
            return MayBe2(f(cast(D, self._value)))
        return cast(MayBe2[U], self)

    def bind[U](self, f: Callable[[D], MayBe2[U]]) -> MayBe2[U]:
        """Flatmap `MayBe2` with function `f`."""
        return f(cast(D, self._value)) if self else cast(MayBe2[U], self)

    def map_except[U](self, f: Callable[[D], U]) -> MayBe2[U]:
        """Map function `f` over contents.

        - if `f` should fail, return a MayBe2()

        - WARNING: Swallows exceptions

        """
        if not self:
            return cast(MayBe2[U], self)
        try:
            return MayBe2(f(cast(D, self._value)))
        except (
            LookupError,
            ValueError,
            TypeError,
            BufferError,
            ArithmeticError,
            RecursionError,
            ReferenceError,
            RuntimeError,
        ):
            return MayBe2()

    def bind_except[U](self, f: Callable[[D], MayBe2[U]]) -> MayBe2[U]:
        """Flatmap `MayBe2` with function `f`.

        - WARNING: Swallows exceptions

        """
        try:
            return f(cast(D, self._value)) if self else cast(MayBe2[U], self)
        except (
            LookupError,
            ValueError,
            TypeError,
            BufferError,
            ArithmeticError,
            RecursionError,
            ReferenceError,
            RuntimeError,
        ):
            return MayBe2()

    @staticmethod
    def call[U, V](f: Callable[[U], V], u: U) -> MayBe2[V]:
        """Return MayBe2 wrapped result of a function call that can fail"""
        try:
            return MayBe2(f(u))
        except (
            LookupError,
            ValueError,
            TypeError,
            BufferError,
            ArithmeticError,
            RecursionError,
            ReferenceError,
            RuntimeError,
        ):
            return MayBe2()

    @staticmethod
    def lz_call[U, V](f: Callable[[U], V], u: U) -> Callable[[], MayBe2[V]]:
        """Return a MayBe2 of a delayed evaluation of a function"""

        def ret() -> MayBe2[V]:
            return MayBe2.call(f, u)

        return ret

    @staticmethod
    def idx[V](v: Sequence[V], ii: int) -> MayBe2[V]:
        """Return a MayBe2 of an indexed value that can fail"""
        try:
            return MayBe2(v[ii])
        except (
            LookupError,
            ValueError,
            TypeError,
            BufferError,
            ArithmeticError,
            RecursionError,
            ReferenceError,
            RuntimeError,
        ):
            return MayBe2()

    @staticmethod
    def lz_idx[V](v: Sequence[V], ii: int) -> Callable[[], MayBe2[V]]:
        """Return a MayBe2 of a delayed indexing of a sequenced type that can fail"""

        def ret() -> MayBe2[V]:
            return MayBe2.idx(v, ii)

        return ret

    @staticmethod
    def sequence[T](itab_mb_d: Iterable[MayBe2[T]]) -> MayBe2[Iterator[T]]:
        """Sequence an indexable of type `MayBe2[~T]`

        * if the iterated `MayBe2` values are not all empty,
          * return a `MayBe2` of an iterator of the contained values
          * otherwise return an empty `MayBe2`

        """
        item: list[T] = []

        for mb_d in itab_mb_d:
            if mb_d:
                item.append(mb_d.get())
            else:
                return MayBe2()

        return MayBe2(iter(item))


# -- class Xor2 -----------------------------------------------------------------

L = TypeVar('L', covariant=True)
R = TypeVar('R', covariant=True)

LEFT = Left()
RIGHT = Right()


class Xor2[L, R]:
    """Either monad - class semantically containing either a left or a right
    value, but not both.

    - implements a left biased Either Monad
      - `Xor2(value: ~L)` or `Xor2(value: ~L, LEFT)` produces a left `Xor2`
      - `Xor2(value: ~L, RIGHT)` produces a right `Xor2`
    - in a Boolean context
      - `True` if a left `Xor2`
      - `False` if a right `Xor2`
    - two `Xor2` objects compare as equal when
      - both are left values or both are right values whose values
        - are the same object
        - compare as equal
    - immutable, an `Xor2` does not change after being created
      - immutable semantics, map & bind return new instances
        - warning: contained value need not be immutable
        - warning: not hashable if value is mutable

    """

    __slots__ = '_value', '_side'
    __match_args__ = ('_value', '_side')

    U = TypeVar('U', covariant=True)
    V = TypeVar('V', covariant=True)
    T = TypeVar('T')

    @overload
    def __new__(cls, value: L) -> Xor2[L, R]: ...
    @overload
    def __new__(cls, value: L, side: Right) -> Xor2[L, R]: ...
    @overload
    def __new__(cls, value: R, side: Left) -> Xor2[L, R]: ...

    def __new__(cls, value: L | R, side: Both = RIGHT) -> Xor2[L, R]:
        return super(Xor2, cls).__new__(cls)

    @overload
    def __init__(self, value: L) -> None: ...
    @overload
    def __init__(self, value: L, side: Left) -> None: ...
    @overload
    def __init__(self, value: R, side: Right) -> None: ...

    def __init__(self, value: L | R, side: Both = LEFT) -> None:
        self._value = value
        self._side = side

    def __hash__(self) -> int:
        return hash((Sentinel('XOR'), self._value, self._side))

    def __bool__(self) -> bool:
        return self._side == LEFT

    def __iter__(self) -> Iterator[L]:
        if self:
            yield cast(L, self._value)

    def __repr__(self) -> str:
        if self:
            return 'Xor2(' + repr(self._value) + ', LEFT)'
        return 'Xor2(' + repr(self._value) + ', RIGHT)'

    def __str__(self) -> str:
        if self:
            return '< ' + str(self._value) + ' | >'
        return '< | ' + str(self._value) + ' >'

    def __len__(self) -> int:
        # An Xor2 always contains just one value.
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
        """Get value if a left.

        - if the `Xor2` is a "left" Xor2
          - return its value
        - if the `Xor2` contains a right value
          - raises `ValueError`
          - best practice is to first check the `Xor2` in a boolean context

        """
        if self._side == RIGHT:
            msg = 'Xor2: get method called on a right valued Xor2'
            raise ValueError(msg)
        return cast(L, self._value)

    def get_left(self) -> MayBe2[L]:
        """Get value of `Xor2` if a left. Safer version of `get` method.

        - if `Xor2` contains a left value, return it wrapped in a MayBe2
        - if `Xor2` contains a right value, return MayBe2()

        """
        if self._side == LEFT:
            return MayBe2(cast(L, self._value))
        return MayBe2()

    def get_right(self) -> MayBe2[R]:
        """Get value of `Xor2` if a right

        - if `Xor2` contains a right value, return it wrapped in a MayBe2
        - if `Xor2` contains a left value, return MayBe2()

        """
        if self._side == RIGHT:
            return MayBe2(cast(R, self._value))
        return MayBe2()

    def map_right[V](self, f: Callable[[R], V]) -> Xor2[L, V]:
        """Construct new Xor2 with a different right."""
        if self._side == LEFT:
            return cast(Xor2[L, V], self)
        return Xor2[L, V](f(cast(R, self._value)), RIGHT)

    def map[U](self, f: Callable[[L], U]) -> Xor2[U, R]:
        """Map over if a left value. Return new instance."""
        if self._side == RIGHT:
            return cast(Xor2[U, R], self)
        return Xor2(f(cast(L, self._value)), LEFT)

    def bind[U](self, f: Callable[[L], Xor2[U, R]]) -> Xor2[U, R]:
        """Flatmap over the left value - propagate right values."""
        if self:
            return f(cast(L, self._value))
        return cast(Xor2[U, R], self)

    def map_except[U](self, f: Callable[[L], U], fallback_right: R) -> Xor2[U, R]:
        """Map over if a left value - with fallback upon exception.

        - if `Xor2` is a left then map `f` over its value
          - if `f` successful return a left `Xor2[U, R]`
          - if `f` unsuccessful return right `Xor2[S, R]`
            - swallows many exceptions `f` may throw at run time
        - if `Xor2` is a right
          - return new `Xor2(right=self._right): Xor2[U, R]`

        """
        if self._side == RIGHT:
            return cast(Xor2[U, R], self)

        applied: MayBe2[Xor2[U, R]] = MayBe2()
        fall_back: MayBe2[Xor2[U, R]] = MayBe2()
        try:
            applied = MayBe2(Xor2(f(cast(L, self._value)), LEFT))
        except (
            LookupError,
            ValueError,
            TypeError,
            BufferError,
            ArithmeticError,
            RecursionError,
            ReferenceError,
            RuntimeError,
        ):
            fall_back = MayBe2(cast(Xor2[U, R], Xor2(fallback_right, RIGHT)))

        if fall_back:
            return fall_back.get()
        return applied.get()

    def bind_except[U](self, f: Callable[[L], Xor2[U, R]], fallback_right: R) ->
    Xor2[U, R]:
        """Flatmap `Xor2` with function `f` with fallback right

        - provide fallback right value if exception thrown.
        - WARNING: Swallows exceptions

        """
        if self._side == RIGHT:
            return cast(Xor2[U, R], self)

        applied: MayBe2[Xor2[U, R]] = MayBe2()
        fall_back: MayBe2[Xor2[U, R]] = MayBe2()
        try:
            if self:
                applied = MayBe2(f(cast(L, self._value)))
        except (
            LookupError,
            ValueError,
            TypeError,
            BufferError,
            ArithmeticError,
            RecursionError,
            ReferenceError,
            RuntimeError,
        ):
            fall_back = MayBe2(cast(Xor2[U, R], Xor2(fallback_right, RIGHT)))

        if fall_back:
            return fall_back.get()
        return applied.get()

    @staticmethod
    def call[T, V](f: Callable[[T], V], left: T) -> Xor2[V, Exception]:
        """Return Xor2 wrapped result of a function call that can fail"""
        try:
            xor = Xor2[V, Exception](f(left), LEFT)
        except (
            LookupError,
            ValueError,
            TypeError,
            BufferError,
            ArithmeticError,
            RecursionError,
            ReferenceError,
            RuntimeError,
        ) as exc:
            xor = Xor2(exc, RIGHT)
        return xor

    @staticmethod
    def lz_call[T, V](f: Callable[[T], V], arg: T) -> Callable[[], Xor2[V, Exception]]:
        """Return an Xor2 of a delayed evaluation of a function"""

        def ret() -> Xor2[V, Exception]:
            return Xor2.call(f, arg)

        return ret

    @staticmethod
    def idx[V](v: Sequence[V], ii: int) -> Xor2[V, Exception]:
        """Return an Xor2 of an indexed value that can fail"""
        try:
            xor = Xor2[V, Exception](v[ii], LEFT)
        except (
            IndexError,
            TypeError,
            ArithmeticError,
            RuntimeError,
        ) as exc:
            xor = Xor2(exc, RIGHT)
        return xor

    @staticmethod
    def lz_idx[V](v: Sequence[V], ii: int) -> Callable[[int], Xor2[V, Exception]]:
        """Return an Xor2 of a delayed indexing of a sequenced type that can fail"""

        def ret(ii: int) -> Xor2[V, Exception]:
            return Xor2.idx(v, ii)

        return ret

    @staticmethod
    def sequence(itab_xor_lr: Iterable[Xor2[L, R]]) -> Xor2[Iterator[L], R]:
        """Sequence an indexable of type `Xor2[~L, ~R]`

        - if the iterated `Xor2` values are all lefts, then
          - return an `Xor2` of an iterable of the left values
        - otherwise return a right Xor2 containing the first right encountered

        """
        ts: list[L] = []

        for xor_lr in itab_xor_lr:
            if xor_lr:
                ts.append(xor_lr.get())
            else:
                return Xor2(xor_lr.get_right().get(), RIGHT)

        return Xor2(iter(ts))
