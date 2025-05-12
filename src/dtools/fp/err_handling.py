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

- *class* MayBe: maybe (optional) monad
- *class* Xor: left biased either monad

"""

from __future__ import annotations

__all__ = ['MayBe', 'Xor', 'LEFT', 'RIGHT']

from collections.abc import Callable, Iterable, Iterator, Sequence
from typing import cast, Final, Never, overload, TypeVar
from .bool import _Bool as Both, _True as Left, _False as Right
from .singletons import Sentinel


# -- class MayBe ------------------------------------------------------------------

D = TypeVar('D', covariant=True)


class MayBe[D]:
    """Maybe monad - class wrapping a potentially missing value.

    - where `MayBe(value)` contains a possible value of type `~D`
    - `MayBe()` semantically represent a non-existent or missing value of type `~D`
    - immutable semantics
      - immutable, therefore made covariant
      - can store any value of any type with one exception
        - if `~D` is `Sentinel`, storing `Sentinel(MayBe)` results in a MayBe()
    - WARNING: hashability invalidated if contained value is not hashable
      - hash function will fail if `MayBe` contains an unhashable value
    - WARNING: unsafe method `get`
      - will raise `ValueError` if MayBe empty and an alt return value not given
      - best practice is to first check the MayBe in a boolean context

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

    def __init__(self, value: D | Sentinel = Sentinel('MayBe')) -> None:
        self._value: D | Sentinel = value

    def __hash__(self) -> int:
        return hash((Sentinel('MayBe'), self._value))

    def __bool__(self) -> bool:
        return self._value is not Sentinel('MayBe')

    def __iter__(self) -> Iterator[D]:
        if self:
            yield cast(D, self._value)

    def __repr__(self) -> str:
        if self:
            return 'MayBe(' + repr(self._value) + ')'
        return 'MayBe()'

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

    def get(self, alt: D | Sentinel = Sentinel('MayBe')) -> D | Never:
        """Return the contained value if it exists, otherwise an alternate value.

        - alternate value must be of type `~D`
        - raises `ValueError` if an alternate value is not provided but needed

        """
        _sentinel: Final[Sentinel] = Sentinel('MayBe')
        if self._value is not _sentinel:
            return cast(D, self._value)
        if alt is _sentinel:
            msg = 'MayBe: an alternate return type not provided'
            raise ValueError(msg)
        return cast(D, alt)

    def map[U](self, f: Callable[[D], U]) -> MayBe[U]:
        """Map function `f` over contents."""

        if self:
            return MayBe(f(cast(D, self._value)))
        return cast(MayBe[U], self)

    def bind[U](self, f: Callable[[D], MayBe[U]]) -> MayBe[U]:
        """Flatmap `MayBe` with function `f`."""
        return f(cast(D, self._value)) if self else cast(MayBe[U], self)

    def map_except[U](self, f: Callable[[D], U]) -> MayBe[U]:
        """Map function `f` over contents.

        - if `f` should fail, return a MayBe()

        - WARNING: Swallows exceptions

        """
        if not self:
            return cast(MayBe[U], self)
        try:
            return MayBe(f(cast(D, self._value)))
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
            return MayBe()

    def bind_except[U](self, f: Callable[[D], MayBe[U]]) -> MayBe[U]:
        """Flatmap `MayBe` with function `f`.

        - WARNING: Swallows exceptions

        """
        try:
            return f(cast(D, self._value)) if self else cast(MayBe[U], self)
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
            return MayBe()

    @staticmethod
    def call[U, V](f: Callable[[U], V], u: U) -> MayBe[V]:
        """Return MayBe wrapped result of a function call that can fail"""
        try:
            return MayBe(f(u))
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
            return MayBe()

    @staticmethod
    def lz_call[U, V](f: Callable[[U], V], u: U) -> Callable[[], MayBe[V]]:
        """Return a MayBe of a delayed evaluation of a function"""

        def ret() -> MayBe[V]:
            return MayBe.call(f, u)

        return ret

    @staticmethod
    def idx[V](v: Sequence[V], ii: int) -> MayBe[V]:
        """Return a MayBe of an indexed value that can fail"""
        try:
            return MayBe(v[ii])
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
            return MayBe()

    @staticmethod
    def lz_idx[V](v: Sequence[V], ii: int) -> Callable[[], MayBe[V]]:
        """Return a MayBe of a delayed indexing of a sequenced type that can fail"""

        def ret() -> MayBe[V]:
            return MayBe.idx(v, ii)

        return ret

    @staticmethod
    def sequence[T](itab_mb_d: Iterable[MayBe[T]]) -> MayBe[Iterator[T]]:
        """Sequence an indexable of type `MayBe[~T]`

        * if the iterated `MayBe` values are not all empty,
          * return a `MayBe` of an iterator of the contained values
          * otherwise return an empty `MayBe`

        """
        item: list[T] = []

        for mb_d in itab_mb_d:
            if mb_d:
                item.append(mb_d.get())
            else:
                return MayBe()

        return MayBe(iter(item))


# -- class Xor -----------------------------------------------------------------

L = TypeVar('L', covariant=True)
R = TypeVar('R', covariant=True)

LEFT = Left()
RIGHT = Right()


class Xor[L, R]:
    """Either monad - class semantically containing either a left or a right
    value, but not both.

    - implements a left biased Either Monad
      - `Xor(value: ~L)` or `Xor(value: ~L, LEFT)` produces a left `Xor`
      - `Xor(value: ~L, RIGHT)` produces a right `Xor`
    - in a Boolean context
      - `True` if a left `Xor`
      - `False` if a right `Xor`
    - two `Xor` objects compare as equal when
      - both are left values or both are right values whose values
        - are the same object
        - compare as equal
    - immutable, an `Xor` does not change after being created
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
    def __new__(cls, value: L) -> Xor[L, R]: ...
    @overload
    def __new__(cls, value: L, side: Right) -> Xor[L, R]: ...
    @overload
    def __new__(cls, value: R, side: Left) -> Xor[L, R]: ...

    def __new__(cls, value: L | R, side: Both = RIGHT) -> Xor[L, R]:
        return super(Xor, cls).__new__(cls)

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
            return 'Xor(' + repr(self._value) + ', LEFT)'
        return 'Xor(' + repr(self._value) + ', RIGHT)'

    def __str__(self) -> str:
        if self:
            return '< ' + str(self._value) + ' | >'
        return '< | ' + str(self._value) + ' >'

    def __len__(self) -> int:
        # An Xor always contains just one value.
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

        - if the `Xor` is a "left" Xor
          - return its value
        - if the `Xor` contains a right value
          - raises `ValueError`
          - best practice is to first check the `Xor` in a boolean context

        """
        if self._side == RIGHT:
            msg = 'Xor: get method called on a right valued Xor'
            raise ValueError(msg)
        return cast(L, self._value)

    def get_left(self) -> MayBe[L]:
        """Get value of `Xor` if a left. Safer version of `get` method.

        - if `Xor` contains a left value, return it wrapped in a MayBe
        - if `Xor` contains a right value, return MayBe()

        """
        if self._side == LEFT:
            return MayBe(cast(L, self._value))
        return MayBe()

    def get_right(self) -> MayBe[R]:
        """Get value of `Xor` if a right

        - if `Xor` contains a right value, return it wrapped in a MayBe
        - if `Xor` contains a left value, return MayBe()

        """
        if self._side == RIGHT:
            return MayBe(cast(R, self._value))
        return MayBe()

    def map_right[V](self, f: Callable[[R], V]) -> Xor[L, V]:
        """Construct new Xor with a different right."""
        if self._side == LEFT:
            return cast(Xor[L, V], self)
        return Xor[L, V](f(cast(R, self._value)), RIGHT)

    def map[U](self, f: Callable[[L], U]) -> Xor[U, R]:
        """Map over if a left value. Return new instance."""
        if self._side == RIGHT:
            return cast(Xor[U, R], self)
        return Xor(f(cast(L, self._value)), LEFT)

    def bind[U](self, f: Callable[[L], Xor[U, R]]) -> Xor[U, R]:
        """Flatmap over the left value - propagate right values."""
        if self:
            return f(cast(L, self._value))
        return cast(Xor[U, R], self)

    def map_except[U](self, f: Callable[[L], U], fallback_right: R) -> Xor[U, R]:
        """Map over if a left value - with fallback upon exception.

        - if `Xor` is a left then map `f` over its value
          - if `f` successful return a left `Xor[U, R]`
          - if `f` unsuccessful return right `Xor[S, R]`
            - swallows many exceptions `f` may throw at run time
        - if `Xor` is a right
          - return new `Xor(right=self._right): Xor[U, R]`

        """
        if self._side == RIGHT:
            return cast(Xor[U, R], self)

        applied: MayBe[Xor[U, R]] = MayBe()
        fall_back: MayBe[Xor[U, R]] = MayBe()
        try:
            applied = MayBe(Xor(f(cast(L, self._value)), LEFT))
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
            fall_back = MayBe(cast(Xor[U, R], Xor(fallback_right, RIGHT)))

        if fall_back:
            return fall_back.get()
        return applied.get()

    def bind_except[U](self, f: Callable[[L], Xor[U, R]], fallback_right: R) -> Xor[U, R]:
        """Flatmap `Xor` with function `f` with fallback right

        - provide fallback right value if exception thrown.
        - WARNING: Swallows exceptions

        """
        if self._side == RIGHT:
            return cast(Xor[U, R], self)

        applied: MayBe[Xor[U, R]] = MayBe()
        fall_back: MayBe[Xor[U, R]] = MayBe()
        try:
            if self:
                applied = MayBe(f(cast(L, self._value)))
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
            fall_back = MayBe(cast(Xor[U, R], Xor(fallback_right, RIGHT)))

        if fall_back:
            return fall_back.get()
        return applied.get()

    @staticmethod
    def call[T, V](f: Callable[[T], V], left: T) -> Xor[V, Exception]:
        """Return Xor wrapped result of a function call that can fail"""
        try:
            xor = Xor[V, Exception](f(left), LEFT)
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
            xor = Xor(exc, RIGHT)
        return xor

    @staticmethod
    def lz_call[T, V](f: Callable[[T], V], arg: T) -> Callable[[], Xor[V, Exception]]:
        """Return an Xor of a delayed evaluation of a function"""

        def ret() -> Xor[V, Exception]:
            return Xor.call(f, arg)

        return ret

    @staticmethod
    def idx[V](v: Sequence[V], ii: int) -> Xor[V, Exception]:
        """Return an Xor of an indexed value that can fail"""
        try:
            xor = Xor[V, Exception](v[ii], LEFT)
        except (
            IndexError,
            TypeError,
            ArithmeticError,
            RuntimeError,
        ) as exc:
            xor = Xor(exc, RIGHT)
        return xor

    @staticmethod
    def lz_idx[V](v: Sequence[V], ii: int) -> Callable[[int], Xor[V, Exception]]:
        """Return an Xor of a delayed indexing of a sequenced type that can fail"""

        def ret(ii: int) -> Xor[V, Exception]:
            return Xor.idx(v, ii)

        return ret

    @staticmethod
    def sequence(itab_xor_lr: Iterable[Xor[L, R]]) -> Xor[Iterator[L], R]:
        """Sequence an indexable of type `Xor[~L, ~R]`

        - if the iterated `Xor` values are all lefts, then
          - return an `Xor` of an iterable of the left values
        - otherwise return a right Xor containing the first right encountered

        """
        ts: list[L] = []

        for xor_lr in itab_xor_lr:
            if xor_lr:
                ts.append(xor_lr.get())
            else:
                return Xor(xor_lr.get_right().get(), RIGHT)

        return Xor(iter(ts))
