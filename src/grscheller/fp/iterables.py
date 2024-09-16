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

D = TypeVar('D')      # D for Data
L = TypeVar('L')      # L for Left
R = TypeVar('R')      # R for Right
S = TypeVar('S')      # S for Sentinel (also used for default values)
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

@overload
def foldL(iterable: Iterable[D],
          f: Callable[[L, D], L],
          init: L,
          sent: S) -> L: ...
@overload
def foldL(iterable: Iterable[D],
          f: Callable[[L, D], L],
          init: L) -> L: ...
@overload
def foldL(iterable: Iterable[D],
          f: Callable[[D, D], D]) -> D|None: ...
@overload
def foldL(iterable: Iterable[D],
          f: Callable[[D, D], D],
          init: D) -> D: ...
def foldL(iterable: Iterable[D],
          f: Callable[[L, D], L],
          init: Optional[L]=None,
          sent: Optional[S]=None) -> L|S|None:
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

    if init is None:
        try:
            acc = cast(L, next(it))
        except StopIteration:
            return sent
    else:
        acc = init

    for v in it:
        acc = f(acc, v)

    return acc

@overload
def foldR(iterable: Reversible[D],
          f: Callable[[D, R], R],
          init: R,
          sent: S) -> R: ...
@overload
def foldR(iterable: Reversible[D],
          f: Callable[[D, R], R],
          init: R) -> R: ...
@overload
def foldR(iterable: Reversible[D],
          f: Callable[[D, D], D]) -> D|None: ...
@overload
def foldR(iterable: Reversible[D],
          f: Callable[[D, D], D],
          init: D) -> D: ...
def foldR(iterable: Reversible[D],
          f: Callable[[D, R], R],
          init: Optional[R]=None,
          sent: Optional[S]=None) -> R|S|None:
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

    if init is None:
        try:
            acc = cast(R, next(it))
        except StopIteration:
            return sent
    else:
        acc = init

    for v in it:
        acc = f(v, acc)

    return acc

def foldL_sc(iterable: Iterable[D|S],
             f: Callable[[L, D], L|S],
             init: Optional[L]=None,
             sent: Optional[S]=None) -> L|S|None:
    """
    #### Shortcut version of foldL.

    * stop fold if sentinel value is encountered
      * if the iterable returns the sentinel value, stop the fold at that point
        * f is never passed the sentinel value
      * if f returns the sentinel value, stop the fold at that point
        * do not include sentinel in fold
    * note that ~S can be the same type as ~L
      * note that when an initial value not given then ~L = ~D
      * if iterable empty & no initial value given, return default
      * None is the "default" sentinel value
    * traditional FP type order given for function f
    * never returns if iterable infinite and sentinel never encountered
    * raises TypeError if the "iterable" is not iterable

    """
    acc: L
    it = iter(iterable)

    if init is None:
        try:
            acc = cast(L, next(it))  # in this case L = D
        except StopIteration:
            return cast(S, sent)  # if sentinel = None, then S is None
    else:
        acc = init

    for d in it:
        if d is sent or d == sent:
            break
        f_ret = f(acc, cast(D, d))
        if f_ret is sent or f_ret == sent:
            break
        acc = cast(L, f_ret)

    return acc

def foldR_sc(iterable: Iterable[D|S],
             f: Callable[[D, R], R],
             init: Optional[R]=None,
             sent: Optional[S]=None,
             pred: Optional[Callable[[D, T], MB[T]]]=None,
             istate: Optional[T]=None) -> R|S|None:
    """
    #### Shortcut version of foldR.

    * stop fold if sentinel value `sent` is encountered
      * if the iterable returns the sentinel value, stop the fold at that point
        * f is never passed the sentinel value
      * if f returns the sentinel value, stop the fold at that point
        * do not include sentinel in fold
        * unlike `foldL_sc`, the fold `f` itself does not "shortcut"
        * predicate `pred` provides a "shortcut" function
          * default `pred` does not "shortcut"
            * ignores the data
            * just passes along the state
    * does not require iterable to be reversible, iterable never "reversed"
    * note that ~S can be the same type as ~R
      * note that when an initial value not given then ~R = ~D
    * traditional FP type order given for function f
    * never returns if iterable infinite and sentinel never encountered
    * raises TypeError if the "iterable" is not iterable
    * does not raise RecursionError, recursion simulated with Python list

    """
    it = iter(iterable)
    if pred is None:
        pred = lambda d, t: MB(t)

    state_mb = MB(istate)

    ds: list[D] = []
    for d in it:
        if d is sent or d == sent:
            break
        else:
            if (state_mb := pred(d, state_mb.get())):
                ds.append(cast(D, d))
            else:
                break

    if init is None:
        if len(ds) == 0:
            return cast(S, sent)  # if sentinel = None, then S is NoneType
        else:
            acc = cast(R, ds.pop())
    else:
        acc = init

    while ds:
        acc = f(ds.pop(), acc)
 
    return acc
