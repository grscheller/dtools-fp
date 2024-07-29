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

"""Library of iterator related functions.

* at all times iterator protocol is assumed to be followed, that is
* all iterators produced are assumed to be iterable
* for all iterators it, iter(it) is it
* iterables are not necessarily iterators

"""

from __future__ import annotations
from typing import Callable, Iterator, Iterable, Optional, Reversible, TypeVar

_D = TypeVar('_D')
_L = TypeVar('_L')
_R = TypeVar('_R')
_S = TypeVar('_S')

__all__ = [ 'concat', 'merge', 'exhaust',
            'foldL', 'foldR', 'sc_foldL',
            'accumulate' ]
__author__ = "Geoffrey R. Scheller"
__copyright__ = "Copyright (c) 2023-2024 Geoffrey R. Scheller"
__license__ = "Apache License 2.0"

## Iterate over multiple Iterables

def concat(*iterables: Iterable[_D]) -> Iterator[_D]:
    """Sequentially concatenate multiple iterators into one.

    * pure Python version of standard library's itertools.chain
    * performant to chain

    """
    iterator: Iterator[_D]
    for iterator in map(lambda x: iter(x), iterables):
        while True:
            try:
                value: _D = next(iterator)
                yield value
            except StopIteration:
                break

def exhaust(*iterables: Iterable[_D]) -> Iterator[_D]:
    """Merge together multiple iterator streams until all are exhausted.

    * returns when last iterator is exhausted

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

def merge(*iterables: Iterable[_D], yield_partials: bool=False) -> Iterator[_D]:
    """Merge multiple iterable streams until one is exhausted.

    * returns when first iterator is exhausted
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

def foldL(iterable: Iterable[_D], f: Callable[[_L, _D], _L],
          default: _S, initial: Optional[_L]=None) -> _L|_S:
    """Folds an iterable from the left with an optional initial value.

    * note that _S can be the same type as _L
    * note that when an initial value is not given then _L = _D
    * if iterable empty & no initial value given, return default
    * traditional FP type order given for function f
    * raises TypeError if the iterable is not iterable (for the benefit of untyped code)
    * never returns if iterable generates an infinite iterator

    """
    acc: _L
    if hasattr(iterable, '__iter__'):
        it = iter(iterable)
    else:
        msg = '"Iterable" is not iterable.'
        raise TypeError(msg)

    if initial is None:
        try:
            acc = next(it)                 # type: ignore # in this case _L = _D
        except StopIteration:
            return default
    else:
        acc = initial

    for v in it:
        acc = f(acc, v)

    return acc

def foldR(iterable: Reversible[_D], f: Callable[[_D, _R], _R],
          default: _S, initial: Optional[_R]=None) -> _R|_S:
    """Folds a reversible iterable from the right with an optional initial value.

    * note that _S can be the same type as _R
    * note that when an initial value not given then _R = _D
    * if iterable empty & no initial value given, return default
    * traditional FP type order given for function f
    * raises TypeError if iterable is not reversible

    """
    acc: _R
    if hasattr(iterable, '__reversed__') or hasattr(iterable, '__len__') and hasattr(iterable, '__getitem__'):
        it = reversed(iterable)
    else:
        msg = 'Iterable is not reversible.'
        raise TypeError(msg)

    if initial is None:
        try:
            acc = next(it)                 # type: ignore # in this case _R = _D
        except StopIteration:
            return default
    else:
        acc = initial

    for v in it:
        acc = f(v, acc)

    return acc

def sc_foldL(iterable: Iterable[_D|_S], f: Callable[[_L, _D|_S], _L],
          sentinel: _S, initial: Optional[_L|_S]=None) -> _L|_S:
    """Folds an iterable from the left with an optional initial value.

    * if the iterable returns the sentinel value, stop the fold at that point
    * if f returns the sentinel value, stop the fold at that point
    * f is never passed the sentinel value
    * note that _S can be the same type as _D
    * if iterable empty & no initial value given, return sentinel
    * note that when initial not given, then _L = _D
    * traditional FP type order given for function f
    * raises TypeError if the iterable is not iterable (for the benefit of untyped code)
    * never returns if iterable generates an infinite iterator & f never returns the sentinel value

    """
    acc: _L|_S
    if hasattr(iterable, '__iter__'):
        it = iter(iterable)
    else:
        msg = '"Iterable" is not iterable.'
        raise TypeError(msg)

    if initial == sentinel:
        return sentinel
    elif initial is None:
        try:
            acc = next(it)                 # type: ignore # in this case _L = _D
        except StopIteration:
            return sentinel
    else:
        acc = initial

    for v in it:
        if v == sentinel:
            break
        facc = f(acc, v)               # type: ignore # if not _L = _S
                                                      # then type(acc) is not _S
        if facc == sentinel:
            break
        else:
            acc = facc
    return acc

def accumulate(iterable: Iterable[_D], f: Callable[[_S, _D], _S],
               initial: Optional[_S]=None) -> Iterator[_S]:
    """Returns an iterator of accumulated values.

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
            acc = it0                      # type: ignore # in this case _S = _D
            for ii in it:
                yield acc
                acc = f(acc, ii)
            yield acc
