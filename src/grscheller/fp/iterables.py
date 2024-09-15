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
from .woException import MB

__all__ = [ 'concat', 'merge', 'exhaust', 'FM',
            'accumulate', 'foldL', 'foldR', 'foldL_sc' ]

class FM(Enum):
    CONCAT = auto()
    MERGE = auto()
    EXHAUST = auto()

D = TypeVar('D')      # D for data
L = TypeVar('L')      # L for left
R = TypeVar('R')      # R for right
S = TypeVar('S')      # S for sentinel (also used for default values)
T = TypeVar('T')      # T for sTate

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
    * itertools.accumulate had mypy issues
    * assumes iterable follows iterable protocol

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

def foldL(iterable: Iterable[D], f: Callable[[L, D], L],
          initial: Optional[L]=None, default: Optional[S]=None) -> L|S:
    """
    #### Folds iterable left with optional initial value.

    * note that ~S can be the same type as ~L
      * note that when an initial value not given then ~L = ~D
      * if iterable empty & no initial value given, return default
    * traditional FP type order given for function f
    * never returns if iterable generates an infinite iterator
    * raises TypeError if the "iterable" is not iterable

    """
    acc: L
    it = iter(iterable)

    if initial is None:
        try:
            acc = cast(L, next(it))  # in this case L = D
        except StopIteration:
            return cast(S, default)  # if default = None, then S is None
    else:
        acc = initial

    for v in it:
        acc = f(acc, v)

    return acc

def foldR(iterable: Reversible[D], f: Callable[[D, R], R],
          initial: Optional[R]=None, default: Optional[S]=None) -> R|S:
    """
    #### Folds reversible iterable right with an optional initial value.

    * note that ~S can be the same type as ~R
      * note that when an initial value not given then ~R = ~D
      * if iterable empty & no initial value given, return default
    * traditional FP type order given for function f
    * raises TypeError if "iterable" is not reversible

    """
    acc: R
    it = reversed(iterable)

    if initial is None:
        try:
            acc = cast(R, next(it))  # in this case R = D
        except StopIteration:
            return cast(S, default)  # if default = None, then S is None
    else:
        acc = initial

    for v in it:
        acc = f(v, acc)

    return acc

def foldL_sc(iterable: Iterable[D|S],
             f: Callable[[L, D], L|S],
             initial: Optional[L]=None, sentinel: Optional[S]=None) -> L|S:
    """
    #### Shortcut version of FoldL.

    * stop fold if sentinel value is encountered
      * if the iterable returns the sentinel value, stop the fold at that point
        * f is never passed the sentinel value
      * if f returns the sentinel value, stop the fold at that point
        * no dot include sentinel in fold
    * note that ~S can be the same type as ~L
      * note that when an initial value not given then ~L = ~D
      * if iterable empty & no initial value given, return default
      * nada: Nada is the "default" default value
    * traditional FP type order given for function f
    * never returns if iterable infinite and sentinel never encountered
    * raises TypeError if the "iterable" is not iterable

    """
    acc: L
    it = iter(iterable)

    if initial is None:
        try:
            acc = cast(L, next(it))  # in this case L = D
        except StopIteration:
            return cast(S, sentinel)  # if sentinel = None, then S is None
    else:
        acc = initial

    for d in it:
        if d is sentinel or d == sentinel:
            break
        f_ret = f(acc, cast(D, d))
        if f_ret is sentinel or f_ret == sentinel:
            break
        acc = cast(L, f_ret)

    return acc

def foldR_sc(iterable: Iterable[D|S],
             f: Callable[[D, R], R],
             initial: Optional[R]=None, sentinel: Optional[S]=None,
             pred: Optional[Callable[[D, T], MB[T]]]=None,
             sTate: Optional[T]=None) -> R|S:
    """
    #### Shortcut version of FoldR. TODO: update docstring

    * does not require iterable to be reversible, iterable never "reversed"
    * stop fold if sentinel value is encountered
      * if the iterable returns the sentinel value
        * start the right fold at that point using initial value if given
        * if an initial value is not given, use previous iterated value
        * if no previous iterated value, return sentinel
    * note that ~S can be the same type as ~R
      * note that when an initial value not given then ~R = ~D
      * if iterable empty & no initial value given, return default
      * nada: Nada is the "default" default value
    * traditional FP type order given for function f
    * never returns if iterable infinite and sentinel never encountered
    * raises TypeError if the "iterable" is not iterable
    * raises RecursionError if maximum recursion depth exceeded

    """
    it = iter(iterable)
    if pred is None:
        pred=lambda d, t: MB(t)

    ds: list[D] = []
    for d in it:
        if d is sentinel or d == sentinel:
            break
        if (mb := pred(cast(D, d), sTate)):
            sTate = mb.get()
            ds.append(cast(D, d))
        else:
            break

    if initial is None:
        if len(ds) == 0:
            #return sentinel   # TODO: do I need the cast?
            return cast(S, sentinel)  # if sentinel = None, then S is None
        else:
            acc = cast(R, ds.pop())
    else:
        acc = initial

    while ds:
        acc = f(ds.pop(), acc)
 
    return acc
