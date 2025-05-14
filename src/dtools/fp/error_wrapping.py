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

- *class* MayBe: maybe (optional) monad
- *class* Xor: left biased either monad

"""

from __future__ import annotations

__all__ = []

from collections.abc import Callable, Sequence
from typing import TypeVar
from dtools.containers.maybe import MayBe
from dtools.containers.xor import Xor, LEFT, RIGHT


D = TypeVar('D', covariant=True)
L = TypeVar('L', covariant=True)
R = TypeVar('R', covariant=True)


def call_or_fail[U, V](f: Callable[[U], V], u: U) -> MayBe[V]:
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


def index_or_fail[V](v: Sequence[V], ii: int) -> MayBe[V]:
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


def call_or_error[T, V](f: Callable[[T], V], left: T) -> Xor[V, Exception]:
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


def index_or_error[V](v: Sequence[V], ii: int) -> Xor[V, Exception]:
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


def lazy_call_or_fail[U, V](f: Callable[[U], V], u: U) -> Callable[[], MayBe[V]]:
    """Return a MayBe of a delayed evaluation of a function"""

    def ret() -> MayBe[V]:
        return MayBe.call(f, u)

    return ret


def lazy_idx_or_fail[V](v: Sequence[V], ii: int) -> Callable[[], MayBe[V]]:
    """Return a MayBe of a delayed indexing of a sequenced type that can fail"""

    def ret() -> MayBe[V]:
        return MayBe.idx(v, ii)

    return ret


def lazy_call_or_error[T, V](
    f: Callable[[T], V], arg: T
) -> Callable[[], Xor[V, Exception]]:
    """Return an Xor of a delayed evaluation of a function"""

    def ret() -> Xor[V, Exception]:
        return Xor.call(f, arg)

    return ret


def lazy_index_or_error[V](
    v: Sequence[V], ii: int
) -> Callable[[int], Xor[V, Exception]]:
    """Return an Xor of a delayed indexing of a sequenced type that can fail"""

    def ret(ii: int) -> Xor[V, Exception]:
        return Xor.idx(v, ii)

    return ret
