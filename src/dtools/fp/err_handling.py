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

__all__ = ['MB', 'XOR']

from collections.abc import Callable, Iterable, Iterator, Sequence
from typing import cast, Final, Never, overload, TypeVar
from .bool import _Bool, _True, _False
from .singletons import Sentinel

D = TypeVar('D')


class MB[D]:
    """Maybe monad - class wrapping a potentially missing value.

    - where `MB(value)` contains a possible value of type `~D`
    - `MB()` semantically represent a non-existent or missing value of type `~D`
    - `MB` objects are self flattening, therefore a `MB` cannot contain a MB
      - `MB(MB(d)) == MB(d)`
      - `MB(MB()) == MB()`
    - immutable semantics, map & bind return new instances
      - warning: hashed values invalidated if contained value is mutated
      - warning: hashed values invalidated if put or pop methods are called
    - unsafe methods `get` and `pop`
      - will raise `ValueError` if MB is empty
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
    def __new__(cls) -> MB[D]: ...
    @overload
    def __new__(cls, value: MB[D]) -> MB[D]: ...
    @overload
    def __new__(cls, value: D) -> MB[D]: ...

    def __new__(cls, value: D | MB[D] | Sentinel = Sentinel('MB')) -> MB[D]:
        return super(MB, cls).__new__(cls)

    @overload
    def __init__(self) -> None: ...
    @overload
    def __init__(self, value: MB[D]) -> None: ...
    @overload
    def __init__(self, value: D) -> None: ...

    def __init__(self, value: D | MB[D] | Sentinel = Sentinel('MB')) -> None:
        self._value: D | Sentinel
        match value:
            case MB(d):
                self._value = d
            case d:
                self._value = d

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
        """Put a value in the MB if empty, if not empty do nothing."""
        if self._value is Sentinel('MB'):
            self._value = value

    def pop(self) -> D | Never:
        """Pop the value if the MB is not empty, otherwise fail."""
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
        except Exception:
            return MB()

    def bind[U](self, f: Callable[[D], MB[U]]) -> MB[U]:
        """Map `MB` with function `f` and flatten."""
        try:
            return f(cast(D, self._value)) if self else MB()
        except Exception:
            return MB()

    @staticmethod
    def call[U, V](f: Callable[[U], V], u: U) -> MB[V]:
        """Return MB wrapped result of a function call that can fail"""
        try:
            return MB(f(u))
        except Exception:
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


True_: Final[_True] = _True()
False_: Final[_False] = _False()

L = TypeVar('L')
R = TypeVar('R')


class XOR[L, R]:
    """Either monad - class semantically containing either a left or a right
    value, but not both.

    - implements a left biased Either Monad
    - `XOR(value: ~L|~R,  /, right: = False )`
      - let `left: ~L` and `right: ~R` then
        - XOR[~L, ~R](left) is a left XOR
        - XOR(right, True) produces a right XOR
    - `XOR(MB(), right)` produces a right `XOR`
    - in a Boolean context
      - `True` if a left `XOR`
      - `False` if a right `XOR`
    - two `XOR` objects compare as equal when
      - both are left values or both are right values whose values
        - are the same object
        - compare as equal
    - immutable, an `XOR` does not change after being created
      - immutable semantics, map & bind return new instances
        - warning: contained values need not be immutable
        - warning: not hashable if value or potential right value mutable

    """

    __slots__ = '_value', '_is_left'
    __match_args__ = ('_value', '_is_left')

    T = TypeVar('T')
    U = TypeVar('U')
    V = TypeVar('V')

    @overload
    def __new__(cls, value: L) -> XOR[L, R]: ...
    @overload
    def __new__(cls, value: L, is_left: _False) -> XOR[L, R]: ...
    @overload
    def __new__(cls, value: R, is_left: _True) -> XOR[L, R]: ...

    def __new__(cls, value: L | R, is_left: _Bool = False_) -> XOR[L, R]:
        return super(XOR, cls).__new__(cls)

    @overload
    def __init__(self, value: L) -> None: ...
    @overload
    def __init__(self, value: L, is_left: _True) -> None: ...
    @overload
    def __init__(self, value: R, is_left: _False) -> None: ...

    def __init__(self, value: L | R, is_left: _Bool = True_) -> None:
        self._value = value
        self._is_left = True_ if is_left else False_

    def __bool__(self) -> bool:
        return bool(self._is_left)

    def __iter__(self) -> Iterator[L]:
        if self:
            yield cast(L, self._value)

    def __repr__(self) -> str:
        if self:
            return 'XOR(' + repr(self._value) + ')'
        return 'XOR(' + repr(self._value) + ', _False())'

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

    @overload
    def get(self) -> MB[L]: ...
    @overload
    def get(self, alt: L) -> MB[L]: ...
    @overload
    def get(self, alt: MB[L]) -> MB[L]: ...

    def get(self, alt: L | MB[L] = MB()) -> MB[L]:
        """Get value if a left.

        - if the `XOR` is a left, return its value
        - if a right, return an alternate value of type ~L` if it is provided
          - alternate value provided directly
          - or optionally provided with a MB
        - returns a `MB[L]` for when an alt value is needed but not provided

        """
        _sentinel = Sentinel('MB')
        match alt:
            case MB(item) if item is not _sentinel:
                if self:
                    return MB(cast(L, self._value))
                return MB(cast(L, item))
            case MB(_):
                if self:
                    return MB(cast(L, self._value))
                return MB()
            case item:
                if self:
                    return MB(cast(L, self._value))
                return MB(item)

    def get_right(self) -> MB[R]:
        """Get value of `XOR` if a right

        - if `XOR` is a right, return a MB of its value
        - if `XOR` is a left, return MB()

        """
        if self:
            return MB()
        return MB(cast(R, self._value))

    def map[U](self, f: Callable[[L], U], failed_map: R) -> XOR[U, R]:
        """Map over if a left value.
        
        TODO: Change to make a right value the exception?

        - if `XOR` is a left then map `f` over its value

          - if `f` successful return a left `XOR[S, R]`
          - if `f` unsuccessful return right `XOR[S, R]`
            - swallows any exceptions `f` may throw
        - if `XOR` is a right
          - return new `XOR(right=self._right): XOR[S, R]`
          - use method `map_right` to adjust the returned value

        """
        if not self:
            return cast(XOR[U, R], self)
        try:
            applied = f(cast(L, self._value))
        except Exception:
            return cast(XOR[U, R], XOR(failed_map, is_left=False_))

        return XOR(applied)

    def map_right(self, g: Callable[[R], R], alt_right: R) -> XOR[L, R]:
        """Map over a right value."""
        if self:
            return self

        try:
            value = g(cast(R, self._value))
        except Exception:
            value = alt_right

        return XOR(value, False_)

    def bind[U](self, f: Callable[[L], XOR[U, R]]) -> XOR[U, R]:
        """Flatmap over the left value

        - map over and then flatten the left value
        - propagate right values

        """
        if self:
            return f(cast(L, self._value))
        return cast(XOR[U, R], self)

    @staticmethod
    def call[U, V](f: Callable[[U], V], left: U) -> XOR[V, Exception]:
        """Return XOR wrapped result of a function call that can fail"""
        try:
            return XOR(f(left))
        except Exception as esc:
            return XOR(esc, is_left=False_)

    @staticmethod
    def lz_call[U, V](f: Callable[[U], V], left: U) -> Callable[[], XOR[V, Exception]]:
        """Return an XOR of a delayed evaluation of a function"""

        def ret() -> XOR[V, Exception]:
            return XOR.call(f, left)

        return ret

    @staticmethod
    def idx[V](v: Sequence[V], ii: int) -> XOR[V, MB[Exception]]:
        """Return an XOR of an indexed value that can fail"""
        try:
            return XOR(v[ii])
        except Exception as esc:
            return XOR(MB(esc), is_left=False_)

    @staticmethod
    def lz_idx[V](v: Sequence[V], ii: int) -> Callable[[], XOR[V, MB[Exception]]]:
        """Return an XOR of a delayed indexing of a sequenced type that can fail"""

        def ret() -> XOR[V, MB[Exception]]:
            return XOR.idx(v, ii)

        return ret

    @staticmethod
    def sequence(itab_xor_lr: Iterable[XOR[L, R]]) -> XOR[Iterator[L], R]:
        """Sequence an indexable of type `XOR[~L, ~R]`

        - if the iterated `XOR` values are all lefts, then
          - return an `XOR` of an iterable of the left values
        - otherwise return a right XOR containing the first right encountered

        """
        ts: list[L] = []

        for xor_lr in itab_xor_lr:
            if (mb := xor_lr.get()):
                ts.append(mb.get())
            else:
                return XOR(xor_lr.get_right().get(), is_left=False_)

        return XOR(iter(ts))
