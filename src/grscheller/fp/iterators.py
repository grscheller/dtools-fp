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

"""Library of iterator related functions."""

from __future__ import annotations
from typing import Callable, Iterator, Iterable, Iterator
from typing import Never, overload, Optional, overload, TypeVar

_T = TypeVar('_T')
_S = TypeVar('_S')

__all__ = ['concat', 'merge', 'exhaust', 'accumulate']
__author__ = "Geoffrey R. Scheller"
__copyright__ = "Copyright (c) 2023-2024 Geoffrey R. Scheller"
__license__ = "Apache License 2.0"

## Iterate over multiple Iterables

def concat(*iterables: Iterable[_T]) -> Iterator[_T]:
    """Sequentially concatenate multiple iterators into one.

    * pure Python version of standard library's itertools.chain
    * performant to chain

    """
    iterator: Iterator[_T]
    for iterator in map(lambda x: iter(x), iterables):
        while True:
            try:
                value: _T = next(iterator)
                yield value
            except StopIteration:
                break

def exhaust(*iterables: Iterable[_T]) -> Iterator[_T]:
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

def merge(*iterables: Iterable[_T], yield_partials: bool=False) -> Iterator[_T]:
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

## accumulate - itertools.accumulate is giving me mypy issues

def accumulate(iterable: Iterable[_T], f: Callable[[_S, _T], _S],
               initial: Optional[_S]=None) -> Iterator[_S]:
    """Returns an iterator of accumulated values.

    * pure Python version of standard library's itertools.accumulate
    * function f does not default to addition (for typing flexibility)
    * begins accumulation with an optional starting value

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
            acc = it0                     # type: ignore # for this case _S = _T
            for ii in it:
                yield acc
                acc = f(acc, ii)
            yield acc
