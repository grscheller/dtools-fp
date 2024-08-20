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

"""
#### Library of iterator related functions.

* iterables are not necessarily iterators
* at all times iterator protocol is assumed to be followed, that is
  * for all iterators `foo` we assume `iter(foo) is foo`
  * all iterators are assumed to be iterable

"""

from __future__ import annotations
from enum import auto, Enum
from typing import Callable, cast, Final, Iterator, Iterable
from typing import overload, Optional, Reversible, TypeVar
from .nada import Nada, nada

__all__ = [ 'accumulate', 'foldL', 'foldR',
            'concat', 'merge', 'exhaust', 'FM' ]

class FM(Enum):
    CONCAT = auto()
    MERGE = auto()
    EXHAUST = auto()

D = TypeVar('D')
L = TypeVar('L')
R = TypeVar('R')
S = TypeVar('S')

## Iterate over multiple Iterables

def concat(*iterables: Iterable[D]) -> Iterator[D]:
    """
    #### Sequentially concatenate multiple iterables together.

    * pure Python version of standard library's itertools.chain
    * iterator yields Sequentially each iterable until all are exhausted
    * an infinite iterable will prevent subsequent iterables from yielding any values
    * performant to chain

    """
    iterator: Iterator[D]
    for iterator in map(lambda x: iter(x), iterables):
        while True:
            try:
                value: D = next(iterator)
                yield value
            except StopIteration:
                break

def exhaust(*iterables: Iterable[D]) -> Iterator[D]:
    """
    #### Shuffle together multiple iterables until all are exhausted.

    * iterator yields until all iterables are exhausted

    """
    iterList = list(map(lambda x: iter(x), iterables))
    if (numIters := len(iterList)) > 0:
        ii = 0
        values = []
        while True:
            try:
                while ii < numIters:
                    values.append(next(iterList[ii]))
                    ii += 1
                for value in values:
                    yield value
                ii = 0
                values.clear()
            except StopIteration:
                numIters -= 1
                if numIters < 1:
                    break
                del iterList[ii]
        for value in values:
            yield value

def merge(*iterables: Iterable[D], yield_partials: bool=False) -> Iterator[D]:
    """
    #### Shuffle together multiple iterables until one is exhausted.

    * iterator yields until one of the iterables is exhausted
    * if yield_partials is true, yield any unmatched yielded values from the other iterables
    * this prevents data lose if any of the iterables are iterators with external references

    """
    iterList = list(map(lambda x: iter(x), iterables))
    if (numIters := len(iterList)) > 0:
        values = []
        while True:
            try:
                for ii in range(numIters):
                    values.append(next(iterList[ii]))
                for value in values:
                    yield value
                values.clear()
            except StopIteration:
                break
        if yield_partials:
            for value in values:
                yield value

## reducing and accumulating

def accumulate(iterable: Iterable[D], f: Callable[[L, D], L],
               initial: Optional[L]=None) -> Iterator[L]:
    """
    #### Returns an iterator of accumulated values.

    * pure Python version of standard library's itertools.accumulate
    * function f does not default to addition (for typing flexibility)
    * begins accumulation with an optional starting value
    * itertools.accumulate has mypy issues

    """
    it = iter(iterable)
    try:
        it0 = next(it)
    except StopIteration:
        if initial is None:
            return
        else:
            yield initial
    else:
        if initial is not None:
            yield initial
            acc = f(initial, it0)
            for ii in it:
                yield acc
                acc = f(acc, ii)
            yield acc
        else:
            acc = cast(L, it0)  # in this case L = D
            for ii in it:
                yield acc
                acc = f(acc, ii)
            yield acc

@overload
def foldL(iterable: Iterable[D], f: Callable[[L, D], L], initial: Optional[L], default: S) -> L|S:
    ...
@overload
def foldL(iterable: Iterable[D], f: Callable[[D, D], D]) -> D|Nada:
    ...
@overload
def foldL(iterable: Iterable[D], f: Callable[[L, D], L], initial: L) -> L:
    ...
@overload
def foldL(iterable: Iterable[D], f: Callable[[L, D], L], initial: Nada) -> Nada:
    ...

def foldL(iterable: Iterable[D], f: Callable[[L, D], L],
          initial: Optional[L]=None, default: S|Nada=nada) -> L|S|Nada:
    """
    #### Folds iterable left with optional initial value.

    * note that ~S can be the same type as ~L
    * note that when an initial value is not given then ~L = ~D
    * if iterable empty & no initial value given, return default
    * traditional FP type order given for function f
    * raises TypeError if the "iterable" is not iterable
    * never returns if iterable generates an infinite iterator

    """
    acc: L
    if hasattr(iterable, '__iter__'):
        it = iter(iterable)
    else:
        msg = '"Iterable" is not iterable.'
        raise TypeError(msg)

    if initial is None:
        try:
            acc = cast(L, next(it))  # in this case L = D
        except StopIteration:
            return cast(S, default)  # if default = nothing, then S is Nothing
    else:
        acc = initial

    for v in it:
        acc = f(acc, v)

    return acc

@overload
def foldR(iterable: Reversible[D], f: Callable[[D, R], R], initial: Optional[R], default: S) -> R|S:
    ...
@overload
def foldR(iterable: Reversible[D], f: Callable[[D, D], D]) -> D|Nothing:
    ...
@overload
def foldR(iterable: Reversible[D], f: Callable[[D, R], R], initial: R) -> R:
    ...
@overload
def foldR(iterable: Reversible[D], f: Callable[[D, R], R], initial: Nada) -> R|Nada:
    ...

def foldR(iterable: Reversible[D], f: Callable[[D, R], R],
          initial: Optional[R]=None, default: S|Nada=nada) -> R|S|Nada:
    """
    #### Folds reversible iterable right with an optional initial value.

    * note that ~S can be the same type as ~R
    * note that when an initial value not given then ~R = ~D
    * if iterable empty & no initial value given, return default
    * traditional FP type order given for function f
    * raises TypeError if iterable is not reversible

    """
    acc: R
    if hasattr(iterable, '__reversed__') or hasattr(iterable, '__len__') and hasattr(iterable, '__getitem__'):
        it = reversed(iterable)
    else:
        msg = 'Iterable is not reversible.'
        raise TypeError(msg)

    if initial is None:
        try:
            acc = cast(R, next(it))  # in this case R = D
        except StopIteration:
            return cast(S, default)  # if default = nothing, then S is Nothing
    else:
        acc = initial

    for v in it:
        acc = f(v, acc)

    return acc

# @overload
# def foldLsc(iterable: Iterable[D|S], f: Callable[[D, D|S], D], sentinel: S) -> D|S: ...
# @overload
# def foldLsc(iterable: Iterable[D|S], f: Callable[[L, D|S], L], sentinel: S, initial: L) -> L: ...
# @overload
# def foldLsc(iterable: Iterable[D|S], f: Callable[[L, D|S], L], sentinel: S, initial: Optional[L]=None) -> L|Nothing: ...
# @overload
# def foldLsc(iterable: Iterable[D|S], f: Callable[[L, D|S], L],
#           initial: Optional[L]=None, default: S|Nothing=nothing) -> L|S: ...
# def foldLsc(iterable: Iterable[D|S], f: Callable[[L, D|S], L],
#           sentinel: S, initial: Optional[L|S]=None) -> L|S:
#     """Folds an iterable from the left with an optional initial value.
# 
#     * if the iterable returns the sentinel value, stop the fold at that point
#     * if f returns the sentinel value, stop the fold at that point
#     * f is never passed the sentinel value
#     * note that _S can be the same type as _D
#     * if iterable empty & no initial value given, return sentinel
#     * note that when initial not given, then _L = _D
#     * traditional FP type order given for function f
#     * raises TypeError if the iterable is not iterable (for the benefit of untyped code)
#     * never returns if iterable generates an infinite iterator & f never returns the sentinel value
# 
#     """
#     acc: L|S
#     if hasattr(iterable, '__iter__'):
#         it = iter(iterable)
#     else:
#         msg = '"Iterable" is not iterable.'
#         raise TypeError(msg)
# 
#     if initial == sentinel:
#         return sentinel
#     elif initial is None:
#         try:
#             acc = cast(L, next(it))
#         except StopIteration:
#             return sentinel
#     else:
#         acc = initial
# 
#     for v in it:
#         if v == sentinel:
#             break
#         facc = f(cast(L, acc), v)                    # if not L = S
#                                                      # then type(acc) is not S
#         if facc == sentinel:
#             break
#         else:
#             acc = facc
#     return acc
