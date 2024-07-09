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
from typing import Iterator, Iterable, Iterator, TypeVar

_T = TypeVar('_T')

__all__ = ['concat', 'exhaust', 'merge']
__author__ = "Geoffrey R. Scheller"
__copyright__ = "Copyright (c) 2023-2024 Geoffrey R. Scheller"
__license__ = "Apache License 2.0"

def concat(*iterables: Iterable[_T]) -> Iterator[_T]:
    """Sequentially concatenate multiple iterators into one.

    * use `itertools.chain` instead
    """
    iterator: Iterator[_T]
    for iterator in map(lambda x: iter(x), iterables):
        while True:
            try:
                value: _T = next(iterator)
                yield value
            except StopIteration:
                break

def merge(*iterables: Iterable[_T], yield_partial: bool=False) -> Iterator[_T]:
    """Merge multiple iterable streams until one is exhausted.

    If `yield_partial` is true, yield any unmatched values from the other
    iterators. This prevents data lose if there are other references to
    non-exhausted iterators floating around.
    """
    iterList = list(map(lambda x: iter(x), iterables))
    if (numIters := len(iterList)) > 0:
        values = []
        # Break when first iterator is exhausted
        while True:
            try:
                for ii in range(numIters):
                    values.append(next(iterList[ii]))
                for value in values:
                    yield value
                values.clear()
            except StopIteration:
                break
        # Yield any remaining values
        if yield_partial:
            for value in values:
                yield value

def exhaust(*iterables: Iterable[_T]) -> Iterator[_T]:
    """Merge multiple iterator streams until all are exhausted."""
    iterList = list(map(lambda x: iter(x), iterables))
    if (numIters := len(iterList)) > 0:
        ii = 0
        values = []
        # Break when last iterator is exhausted
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
        # Yield any remaining values
        for value in values:
            yield value
